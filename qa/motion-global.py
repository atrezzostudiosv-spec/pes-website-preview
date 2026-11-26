import json, threading, subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'global-motion-qa';OUT.mkdir(exist_ok=True)
BASELINE=Path('/tmp/pes-global-motion-baseline')
subprocess.run(['git','worktree','add','--detach',str(BASELINE),'f7a53a80178ed3d117c22c415277346d2a0f3a26'],cwd=ROOT,check=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
def serve(path):
    s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(path),**kw))
    threading.Thread(target=s.serve_forever,daemon=True).start()
    return f'http://127.0.0.1:{s.server_port}/'
BASE=serve(ROOT); OLD=serve(BASELINE)
PAGES=['','about/','portfolio/','capabilities/','careers/','contact/','hillside/']+['capabilities/'+x+'/' for x in ['lighting-systems','automated-window-coverings','lighting-design','power-quality-and-energy-management','ev-charging']]+['careers/'+x+'/' for x in ['foreman','journeyman','electrician','apprentice']]
results=[];failures=[]
def load(p,url):
    assert p.goto(url,wait_until='domcontentloaded',timeout=25000).ok
    p.evaluate('document.fonts.ready')
def snap(p):
    return p.evaluate("""()=>{let m=document.querySelector('main');let rect=e=>{let r=e.getBoundingClientRect();return [r.x,r.y+scrollY,r.width,r.height].map(x=>Math.round(x*100)/100)};return {text:m.innerText,headings:[...m.querySelectorAll('h1,h2,h3')].map(e=>[e.innerText,getComputedStyle(e).fontWeight,getComputedStyle(e).fontFamily,rect(e)]),links:[...m.querySelectorAll('a')].map(e=>[e.getAttribute('href'),e.innerText]),regions:[...m.querySelectorAll('section')].map(rect),overflow:document.documentElement.scrollWidth>innerWidth}}""")
def check(a,b):
    assert a['text']==b['text'] and a['links']==b['links'],'copy/link change'
    assert len(a['headings'])==len(b['headings']) and len(a['regions'])==len(b['regions'])
    for x,y in zip(a['headings'],b['headings']):
        assert x[:3]==y[:3],(x[:3],y[:3])
        assert all(abs(v-w)<=1.5 for v,w in zip(x[3],y[3])),(x,y)
    for x,y in zip(a['regions'],b['regions']):
        assert all(abs(v-w)<=1.5 for v,w in zip(x,y)),(x,y)
def test(b,path,w):
    tag=(path.strip('/').replace('/','-') or 'home')+'-'+str(w)
    v={'width':w,'height':844 if w<768 else 900}
    old=b.new_page(viewport=v,java_script_enabled=False)
    static=b.new_page(viewport=v,java_script_enabled=False)
    p=b.new_page(viewport=v)
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if 'PES group fallback' in m.text or 'PES heading fallback' in m.text else None)
    try:
        load(old,OLD+path);load(static,BASE+path)
        if path=='' and static.locator('.pes-featured-split').count():
            # Home 03 is an intentional, independently tested component replacement.
            # Restore baseline HTML only in this static comparison browser, never on disk.
            feature=old.locator('.project-feature').evaluate("e=>e.outerHTML")
            static.locator('.pes-featured-split').evaluate("(e,html)=>e.outerHTML=html",feature)
            static.locator('.pes-cinematic-interlude').evaluate_all('els=>els.forEach(e=>e.remove())')
        check(snap(old),snap(static))
        load(p,BASE+path)
        p.wait_for_function("document.querySelector('[data-pes-editorial]')?.dataset.pesEditorialReady==='true'")
        assert p.locator('[data-pes-editorial]').count()>0
        assert p.locator('.hero-film [data-am-text],.ats2-scope [data-am-text],.ss03 [data-am-text]').count()==0
        assert p.locator('.pes-motion-staging').count()==0
        # Scroll to each opted-in region; original motors operate on unchanged nodes.
        regions=p.locator('[data-pes-editorial]')
        for i in range(regions.count()):
            r=regions.nth(i)
            r.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-100,behavior:'instant'})")
            p.wait_for_timeout(100)
        # Traverse the document to expose individually observed units in long sections.
        p.evaluate("""async()=>{const step=Math.max(200,innerHeight*.55);for(let y=0;y<document.documentElement.scrollHeight;y+=step){window.scrollTo({top:y,behavior:'instant'});await new Promise(r=>setTimeout(r,45));}}""")
        p.wait_for_timeout(2200)
        assert p.locator('[data-pes-motion-done]').count()>0
        assert p.locator('.pes-global-title-overlay').count()==0,'unrestored heading'
        assert not p.locator('[data-pes-editorial]').evaluate_all("els=>els.some(e=>Array.from(e.querySelectorAll('h1,h2,p,a')).some(x=>!x.closest('.ss03,.ats2-scope,form,fieldset')&&getComputedStyle(x).opacity==='0'))"),'invisible editorial content'
        assert not errors,errors
        p.evaluate("window.scrollTo({top:0,behavior:'instant'})");p.wait_for_timeout(120)
        p.screenshot(path=str(OUT/(tag+'.png')))
        results.append({'page':path,'width':w,'regions':regions.count(),'completed':p.locator('[data-pes-motion-done]').count()})
    except Exception as e:
        failures.append({'page':path,'width':w,'error':str(e)});print('FAIL',tag,e,flush=True)
        p.screenshot(path=str(OUT/(tag+'-failure.png')))
    finally:old.close();static.close();p.close()
def fallback(b,path,w):
    p=b.new_page(viewport={'width':w,'height':844},reduced_motion='reduce')
    try:
        load(p,BASE+path);p.wait_for_timeout(100)
        assert p.locator('.pes-global-title-overlay,.pes-motion-staging,[data-pes-editorial-ready]').count()==0
        assert p.locator('[data-pes-editorial]').count()>0
        results.append({'page':path,'width':w,'reduced':True})
    except Exception as e:failures.append({'page':path,'width':w,'reduced':True,'error':str(e)})
    finally:p.close()
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True)
    for path in PAGES:
        for w in [375,1440]:test(b,path,w)
        fallback(b,path,375)
    for w in [768,1024]:
        for path in ['','about/','capabilities/','careers/','contact/']:test(b,path,w)
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
if failures:raise SystemExit(1)
