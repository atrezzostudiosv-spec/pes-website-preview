import json, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'split-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
REF='https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-SEC-002'
SEL='[data-atz-id="ATZ-SEC-002"]'
results=[];failures=[]
def state(p):
    return p.locator(SEL).evaluate("""root=>{let s=root.querySelector('.ats-scene'),stage=s.querySelector('.ats-stage'),img=s.querySelector('img'),copy=s.querySelector('.ats-split-copy'),pic=s.querySelector('.ats-split-image');let r=e=>{let x=e.getBoundingClientRect();return {x:x.x,y:x.y,w:x.width,h:x.height,right:x.right,bottom:x.bottom}};let v=n=>s.style.getPropertyValue(n);return {p:Number(s.dataset.atsProgress),clip:v('--ats-image-clip'),alpha:v('--ats-copy-alpha'),x:v('--ats-copy-x'),height:s.offsetHeight,stage:stage.offsetHeight,sticky:getComputedStyle(stage).position,clipCss:getComputedStyle(pic).clipPath,opacity:getComputedStyle(copy).opacity,copy:r(copy),img:r(img),imageLoaded:img.complete&&img.naturalWidth>0,overflow:document.documentElement.scrollWidth>innerWidth,background:getComputedStyle(stage).backgroundColor,filter:getComputedStyle(img).filter}}""")
def seek(p,q):
    p.locator(SEL+' .ats-scene').evaluate("(s,q)=>window.scrollTo({top:s.getBoundingClientRect().top+scrollY+q*(s.offsetHeight-innerHeight),behavior:'instant'})",q)
    p.wait_for_timeout(230)
def load(p,url):
    assert p.goto(url,wait_until='domcontentloaded',timeout=30000).ok
    p.evaluate('document.fonts.ready')
def compare(b,w,h):
    ref=b.new_page(viewport={'width':w,'height':h})
    p=b.new_page(viewport={'width':w,'height':h})
    errors=[];bad=[]
    p.on('pageerror',lambda e:errors.append(str(e)))
    p.on('response',lambda r:bad.append(r.url) if r.status>=400 and r.url.startswith(BASE) else None)
    try:
        for page,url in [(ref,REF),(p,BASE)]:
            load(page,url)
            page.wait_for_function("document.querySelector('[data-atz-id=ATZ-SEC-002]')?.classList.contains('ats-enhanced')")
        p.wait_for_function("document.querySelector('[data-atz-id=ATZ-SEC-004]')?.__atrezzoScrollSections02")
        assert p.locator(SEL+' [data-am-text],'+SEL+' [data-pes-editorial]').count()==0
        assert p.locator(SEL).evaluate("e=>e.previousElementSibling?.matches('section.pes-specialty')||e.previousElementSibling?.matches('script')||e.previousElementSibling?.classList.contains('pes-specialty')")
        assert p.locator(SEL).evaluate("e=>e.nextElementSibling.classList.contains('art-atlas')")
        for i,q in enumerate([0,.25,.5,.75,1,.5,0]):
            seek(ref,q);seek(p,q)
            ref.locator(SEL+' img').evaluate("e=>e.decode().catch(()=>{})")
            p.locator(SEL+' img').evaluate("e=>e.decode()")
            a,c=state(ref),state(p)
            assert a['height']==c['height'] and a['stage']==c['stage'],(a,c)
            # Browser scroll offsets are quantized to device pixels; compare numerical output at the measured progress.
            assert abs(a['p']-c['p'])<.005 and abs(float(a['clip'].rstrip('%'))-float(c['clip'].rstrip('%')))<=.3 and abs(float(a['alpha'])-float(c['alpha']))<=.02 and abs(float(a['x'].removesuffix('px'))-float(c['x'].removesuffix('px')))<=.6,(q,a,c)
            assert c['sticky']=='sticky' and c['imageLoaded'] and not c['overflow']
            assert c['background']=='rgb(0, 0, 0)' and c['filter']=='none'
            if w<=780:assert c['clipCss']=='inset(0px)',c
            if q==1:
                assert c['opacity']=='1' and c['copy']['x']>=0 and c['copy']['right']<=w+1 and c['copy']['bottom']<=h+1,c
                assert p.locator(SEL+' h2').evaluate("e=>getComputedStyle(e).fontWeight")=='700'
                assert 'Montserrat' in p.locator(SEL+' h2').evaluate("e=>getComputedStyle(e).fontFamily")
                assert p.locator(SEL+' h2').evaluate("e=>getComputedStyle(e,'::after').height")=='2px'
            p.screenshot(path=str(OUT/f'pes-{w}-{h}-{i}.png'))
            ref.screenshot(path=str(OUT/f'ref-{w}-{h}-{i}.png'))
            results.append({'width':w,'height':h,'q':q,'reference':a,'pes':c})
        # Keyboard reveal at start, even when scroll-driven text alpha is zero.
        seek(p,0)
        link=p.locator(SEL+' a');link.focus()
        assert link.evaluate("e=>document.activeElement===e")
        assert p.locator(SEL+' .ats-split-copy').evaluate("e=>getComputedStyle(e).opacity")=='1'
        assert link.get_attribute('href')=='hillside/'
        assert link.evaluate("e=>getComputedStyle(e).outlineStyle")!='none'
        p.screenshot(path=str(OUT/f'focus-{w}-{h}.png'))
        link.evaluate("e=>e.blur()")
        p.locator(SEL).evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-180,behavior:'instant'})")
        p.wait_for_timeout(250);p.screenshot(path=str(OUT/f'entry-{w}-{h}.png'))
        p.locator(SEL).evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().bottom+scrollY-innerHeight*.8,behavior:'instant'})")
        p.wait_for_timeout(250);p.screenshot(path=str(OUT/f'exit-{w}-{h}.png'))
        assert not errors and not bad,(errors,bad)
    except Exception as e:failures.append({'width':w,'height':h,'error':str(e)});print('FAIL',w,h,e,flush=True);p.screenshot(path=str(OUT/f'failure-{w}-{h}.png'))
    finally:p.close();ref.close()
def fallback(b,w,reduce):
    p=b.new_page(viewport={'width':w,'height':844},java_script_enabled=reduce,reduced_motion='reduce' if reduce else 'no-preference')
    try:
        load(p,BASE)
        p.locator(SEL).evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY,behavior:'instant'})")
        p.wait_for_timeout(250)
        c=state(p)
        assert c['opacity']=='1' and c['sticky']=='relative' and c['imageLoaded'],c
        if w<=780:assert c['clipCss']=='inset(0px)',c
        assert p.locator(SEL+' a').is_visible()
        p.screenshot(path=str(OUT/f'fallback-{w}-{reduce}.png'))
        results.append({'fallback':reduce,'width':w,'pes':c})
    except Exception as e:failures.append({'fallback':reduce,'width':w,'error':str(e)});print('FAIL fallback',w,reduce,e,flush=True)
    finally:p.close()
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True)
    for w,h in [(375,844),(390,844),(768,900),(1024,768),(1440,900),(1920,1080)]:compare(b,w,h)
    for w in [375,1440]:
        for reduce in [True,False]:fallback(b,w,reduce)
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
if failures:raise SystemExit(1)
