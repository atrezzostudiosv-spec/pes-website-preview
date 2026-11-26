import base64, json, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'cinematic-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw));threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{srv.server_port}/';SEL='.pes-cinematic-interlude'
REF='https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-SCR-007'
results=[];failures=[]
def go(p,url):
    assert p.goto(url,wait_until='load',timeout=45000).ok
    p.evaluate('document.fonts.ready')
def getstate(p):
    return p.locator(SEL).evaluate("""r=>{const st=ScrollTrigger.getAll().find(t=>t.pin===r);const grid=r.querySelector('.grid');const title=r.querySelector('.content__title');const h=title.querySelector('h2');const box=e=>{let b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,bottom:b.bottom}};return {progress:st.progress,start:st.start,end:st.end,scale:gsap.getProperty(grid,'scaleX'),skew:gsap.getProperty(grid,'skewY'),gridOpacity:Number(getComputedStyle(grid).opacity),titleOpacity:Number(getComputedStyle(title).opacity),title:box(title),root:box(r),next:box(r.closest('.pin-spacer')?.nextElementSibling||r.nextElementSibling),header:box(document.querySelector('.site-header')),overflow:document.documentElement.scrollWidth>innerWidth,weight:getComputedStyle(h).fontWeight,bold:getComputedStyle(h.querySelector('strong')).fontWeight,line:getComputedStyle(h,'::after').height,background:getComputedStyle(r).backgroundColor,services:getComputedStyle(document.querySelector('.art-atlas')).backgroundColor,assets:[...grid.children].map(e=>getComputedStyle(e).backgroundImage)}}""")
def seek(p,q):
    p.locator(SEL).evaluate("(r,q)=>{const s=ScrollTrigger.getAll().find(t=>t.pin===r);window.scrollTo({top:s.start+q*(s.end-s.start),behavior:'instant'});}",q)
    p.wait_for_timeout(850)
def run(b,name,w,h):
    tag=f'{name}-{w}';p=b.new_page(viewport={'width':w,'height':h},is_mobile=(name=='webkit' and w<701),has_touch=(w<701))
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
        go(p,BASE);p.wait_for_function("window.ScrollTrigger && document.querySelector('.pes-cinematic-interlude').classList.contains('pes-cinematic-animated')",timeout=25000)
        p.wait_for_function("ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))")
        assert p.locator(SEL+' .grid__img').count()==9
        assert p.locator(SEL+' h2').inner_text().replace('\n',' ')=='Powered by Precision.'
        assert p.locator(SEL+' [data-am-text],'+SEL+' [data-pes-editorial]').count()==0
        assert p.locator('script[src*="gsap.min.js"]').count()==1 and p.locator('script[src*="ScrollTrigger.min.js"]').count()==1
        assert p.locator(SEL).evaluate("""async r=>{const urls=[...r.querySelectorAll('.grid__img')].map(e=>getComputedStyle(e).backgroundImage.match(/url\(["']?(.*?)["']?\)/)[1]);return (await Promise.all(urls.map(async u=>{const i=new Image();i.src=u;await i.decode();return i.naturalWidth>0}))).every(Boolean)}""")
        states=[]
        for i,q in enumerate([.01,.38,.67,1,.5,.01]):
            seek(p,q);s=getstate(p)
            assert abs(s['progress']-q)<.03,(q,s)
            assert abs((s['end']-s['start'])-h*(.58 if w<=700 else 1))<5,s
            assert not s['overflow'] and s['weight']=='300' and s['bold']=='700' and s['line']=='2px',s
            assert s['background']=='rgb(0, 0, 0)' and s['services']=='rgb(0, 0, 0)',s
            if q==.01:assert s['scale']<1 and s['gridOpacity']>.95,s
            if q==.38:assert s['titleOpacity']>.5,s
            if q==1:assert s['gridOpacity']<.025 and s['titleOpacity']<.025,s
            if q==.5:assert s['gridOpacity']>.5 and s['titleOpacity']>.5,s
            assert abs((s['title']['x']+s['title']['w']/2)-w/2)<3,s
            states.append(s);p.screenshot(path=str(OUT/f'{tag}-{i}.jpg'),type='jpeg',quality=82)
        assert abs(states[0]['scale']-states[-1]['scale'])<.04,states
        assert max(abs(x['header']['y']-states[0]['header']['y']) for x in states)<2
        seek(p,1)
        assert abs(getstate(p)['next']['y']-getstate(p)['root']['bottom'])<3
        p.evaluate("window.scrollBy({top:Math.round(innerHeight*.35),behavior:'instant'})");p.wait_for_timeout(250)
        p.screenshot(path=str(OUT/f'{tag}-exit.jpg'),type='jpeg',quality=82)
        assert not errors,errors
        results.append({'browser':name,'width':w,'height':h,'states':states})
    except Exception as e:
        failures.append({'browser':name,'width':w,'error':str(e)});print('FAIL',tag,str(e)[:1200],flush=True);p.screenshot(path=str(OUT/f'{tag}-failure.jpg'),type='jpeg',quality=82)
    finally:p.close()
def fallback(b,w,reduce):
    p=b.new_page(viewport={'width':w,'height':844},java_script_enabled=reduce,reduced_motion='reduce' if reduce else 'no-preference')
    try:
        go(p,BASE);p.locator(SEL).scroll_into_view_if_needed()
        assert p.locator(SEL).evaluate("e=>!e.classList.contains('pes-cinematic-animated')&&getComputedStyle(e.querySelector('.grid')).opacity==='1'&&getComputedStyle(e.querySelector('.content__title')).opacity==='1'")
        assert p.locator(SEL+' .grid__img').count()==9
        assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
        p.screenshot(path=str(OUT/f'fallback-{w}-{reduce}.jpg'),type='jpeg',quality=82)
        results.append({'fallback':reduce,'width':w})
    except Exception as e:failures.append({'fallback':reduce,'width':w,'error':str(e)})
    finally:p.close()
def reference(b):
    p=b.new_page(viewport={'width':1440,'height':900})
    try:
        go(p,REF);p.wait_for_function("window.ScrollTrigger && ScrollTrigger.getAll().some(t=>t.pin?.matches('[data-atz-id=ATZ-SCR-007]'))",timeout=30000)
        for i,q in enumerate([0,.5,1]):
            p.evaluate("q=>{const s=ScrollTrigger.getAll().find(t=>t.pin?.matches('[data-atz-id=ATZ-SCR-007]'));window.scrollTo({top:s.start+q*(s.end-s.start),behavior:'instant'})}",q);p.wait_for_timeout(850)
            p.screenshot(path=str(OUT/f'reference-{i}.jpg'),type='jpeg',quality=82)
        results.append({'reference':True})
    except Exception as e:failures.append({'reference':True,'error':str(e)});print('REFERENCE FAIL',e,flush=True)
    finally:p.close()
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True)
    reference(b)
    for w,h in [(375,844),(390,844),(768,900),(1024,768),(1440,900),(1920,1080)]:run(b,'chromium',w,h)
    for w in [375,1440]:
        for reduce in [False,True]:fallback(b,w,reduce)
    b.close()
    b=pw.webkit.launch(headless=True)
    for w,h in [(375,844),(390,844)]:run(b,'webkit',w,h)
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
# Small contact sheet to inspect directly from the log. Full viewport captures stay in artifacts.
files=[OUT/f'{browser}-{w}-{i}.jpg' for browser,w in [('chromium',1440),('chromium',390),('webkit',390)] for i in [0,1,2,3]]
sheet=Image.new('RGB',(800,3*245),(15,15,15));d=ImageDraw.Draw(sheet)
for k,f in enumerate(files):
    if not f.exists():continue
    im=Image.open(f);im.thumbnail((195,215));x=(k%4)*200;y=(k//4)*245
    sheet.paste(im,(x+(195-im.width)//2,y));d.text((x+3,y+218),f.stem,fill='white')
sheet.save(OUT/'contact-sheet.jpg',quality=65)
print('EVIDENCE_THUMB '+base64.b64encode((OUT/'contact-sheet.jpg').read_bytes()).decode(),flush=True)
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
if failures:raise SystemExit(1)
