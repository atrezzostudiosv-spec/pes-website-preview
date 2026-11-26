import json, threading, math
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'film-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=s.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{s.server_port}/'
REF='https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-SEC-005'
WIDTHS=[375,390,768,1024,1180,1181,1440,1920]
results=[];failures=[]
def state(p):
    return p.evaluate("""()=>{let s=document.querySelector('.ats2-film-scene'),h=s.querySelector('.ats2-film-header'),t=s.querySelector('.ats2-film-track'),v=s.querySelector('.ats2-film-viewport'),title=s.querySelector('h2'),st=s.querySelector('.ats2-stage'),a=s.querySelector('article');const r=e=>{const x=e.getBoundingClientRect();return {x:x.x,y:x.y,w:x.width,h:x.height,bottom:x.bottom,right:x.right}};return {p:Number(s.dataset.ats2Progress),active:Number(s.dataset.ats2Active),x:parseFloat(s.style.getPropertyValue('--ats2-film-x')),distance:t.scrollWidth-v.clientWidth,scene:s.offsetHeight,stage:st.offsetHeight,header:h.offsetHeight,title:title.offsetHeight,titleFont:getComputedStyle(title).fontSize,titleLine:getComputedStyle(title).lineHeight,titleWidth:title.getBoundingClientRect().width,frame:a.offsetHeight,frameWidth:a.offsetWidth,viewport:innerWidth,sticky:getComputedStyle(st).position,headerRect:r(h),titleRect:r(title),subtitleRect:r(s.querySelector('.ats2-film-subtitle')),counterRect:r(s.querySelector('.ats2-film-counter')),frameRect:r(a),imageLoaded:[...s.querySelectorAll('img')].every(x=>x.complete&&x.naturalWidth>0),horizontalOverflow:document.documentElement.scrollWidth>innerWidth}}""")
def seek(p,q):
    p.evaluate("""q=>{const s=document.querySelector('.ats2-film-scene');window.scrollTo({top:s.getBoundingClientRect().top+scrollY+q*(s.offsetHeight-innerHeight),behavior:'instant'})}""",q)
    p.wait_for_timeout(500)
def compare(b,w):
    h=844 if w<768 else 900
    ref=b.new_page(viewport={'width':w,'height':h})
    pes=b.new_page(viewport={'width':w,'height':h})
    errors=[];bad=[]
    pes.on('pageerror',lambda e:errors.append(str(e)))
    pes.on('response',lambda r:bad.append(r.url) if r.status>=400 and r.url.startswith(BASE) else None)
    try:
        for p,u in [(ref,REF),(pes,BASE)]:
            assert p.goto(u,wait_until='domcontentloaded',timeout=30000).ok
            p.wait_for_function("document.querySelector('[data-atz-id=\"ATZ-SEC-005\"]')?.classList.contains('ats2-enhanced')")
            p.evaluate('document.fonts.ready')
        pes.wait_for_function("Array.from(document.querySelectorAll('[data-atz-id]')).every(e=>e.__atrezzoScrollSections02)")
        assert pes.locator('[data-atz-id="ATZ-SEC-005"] .ats2-film-frame').count()==3
        assert pes.locator('[data-atz-id="ATZ-SEC-005"]').evaluate("(e)=>e.nextElementSibling.classList.contains('project-feature')")
        for i,q in enumerate([0,.25,.5,.75,1,.5,0]):
            seek(ref,q);seek(pes,q)
            r=state(ref);c=state(pes)
            rec={'width':w,'step':i,'q':q,'reference':r,'pes':c}
            results.append(rec)
            ref.screenshot(path=str(OUT/f'reference-{w}-{i}.png'))
            pes.screenshot(path=str(OUT/f'pes-{w}-{i}.png'))
            assert r['scene']==c['scene'] and r['stage']==c['stage'] and r['frameWidth']==c['frameWidth'] and r['distance']==c['distance'],rec
            assert abs(r['p']-c['p'])<.005 and abs(r['x']-c['x'])<4 and r['active']==c['active'],rec
            assert c['sticky']=='sticky' and not c['horizontalOverflow'] and c['imageLoaded'],rec
            assert c['titleRect']['right']<=w+1 and c['subtitleRect']['right']<=w+1,rec
        pes.evaluate("""()=>{const s=document.querySelector('[data-atz-id="ATZ-SEC-004"]');window.scrollTo({top:s.getBoundingClientRect().top+scrollY+Math.max(0,s.offsetHeight-innerHeight)*.5,behavior:'instant'})}""")
        pes.wait_for_timeout(500)
        assert pes.locator('[data-atz-id="ATZ-SEC-004"]').evaluate("(e)=>e.classList.contains('ats2-reduced')") if w<=820 else pes.locator('[data-atz-id="ATZ-SEC-004"] .ats2-scene').evaluate("(e)=>Number(e.dataset.ats2Progress)>.45 && Number(e.dataset.ats2Progress)<.55")
        pes.screenshot(path=str(OUT/f'004-{w}.png'))
        assert not errors and not bad,(errors,bad)
    except Exception as e:
        failures.append({'width':w,'error':str(e)})
        print('FAIL',w,str(e),flush=True)
    finally:ref.close();pes.close()
def fallback(b,w,reduced):
    p=b.new_page(viewport={'width':w,'height':844},reduced_motion='reduce' if reduced else 'no-preference',java_script_enabled=reduced)
    try:
        p.goto(BASE,wait_until='domcontentloaded')
        p.wait_for_timeout(400)
        v=p.locator('[data-atz-id="ATZ-SEC-005"]').evaluate("""e=>({enhanced:e.classList.contains('ats2-enhanced'),frames:[...e.querySelectorAll('article')].map(x=>({height:x.offsetHeight,width:x.offsetWidth,transform:getComputedStyle(x).transform})),track:getComputedStyle(e.querySelector('.ats2-film-track')).transform,sticky:getComputedStyle(e.querySelector('.ats2-stage')).position})""")
        assert not v['enhanced'] and v['track']=='none' and v['sticky']=='relative' and len(v['frames'])==3 and all(x['height']>0 and x['width']>0 for x in v['frames']),v
        p.locator('[data-atz-id="ATZ-SEC-005"]').screenshot(path=str(OUT/f'fallback-{w}-{reduced}.png'))
        results.append({'fallback':reduced,'width':w,'metrics':v})
    except Exception as e:failures.append({'fallback':reduced,'width':w,'error':str(e)})
    finally:p.close()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    for w in WIDTHS:compare(b,w)
    for w in [375,1440]:
        fallback(b,w,True);fallback(b,w,False)
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
print(json.dumps(failures),flush=True)
if failures:raise SystemExit(1)
