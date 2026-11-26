import json, threading, subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'motion-qa';OUT.mkdir(exist_ok=True)
BASELINE=Path('/tmp/pes-motion-baseline')
subprocess.run(['git','worktree','add','--detach',str(BASELINE),'e2f7406ce41c699033464e01adfcdf1e063332d0'],cwd=ROOT,check=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
def serve(path):
    s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(path),**kw))
    threading.Thread(target=s.serve_forever,daemon=True).start()
    return f'http://127.0.0.1:{s.server_port}/'
BASE=serve(ROOT); OLD=serve(BASELINE)
results=[]; failures=[]
SEL='.pes-specialty'
def geometry(p):
    return p.locator(SEL).evaluate("""s=>{const b=s.getBoundingClientRect();const q=e=>{const r=e.getBoundingClientRect(),c=getComputedStyle(e);return {x:r.x-b.x,y:r.y-b.y,w:r.width,h:r.height,font:c.fontSize,weight:c.fontWeight,family:c.fontFamily}};return {section:q(s),heading:q(s.querySelector('h2')),bold:q(s.querySelector('h2 strong')),label:q(s.querySelector('.pes-specialty-label')),copy:q(s.querySelector('.pes-specialty-copy')),paragraphs:[...s.querySelectorAll('.pes-specialty-copy p')].map(q),link:q(s.querySelector('a')),grid:q(s.querySelector('.pes-specialty-grid')),overflow:document.documentElement.scrollWidth>innerWidth,headingCount:s.querySelectorAll('h2').length}}""")
def go(p,url):
    assert p.goto(url,wait_until='domcontentloaded',timeout=30000).ok
    p.evaluate('document.fonts.ready')
def scroll(p):
    p.locator(SEL).evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-100,behavior:'instant'})")
def assert_same(a,b):
    for k in ['section','heading','bold','label','copy','link','grid']:
        for dim in ['x','y','w','h']:
            assert abs(a[k][dim]-b[k][dim])<=1.5,(k,dim,a[k],b[k])
        for prop in ['font','weight','family']:
            assert a[k][prop]==b[k][prop],(k,prop,a[k],b[k])
    for x,y in zip(a['paragraphs'],b['paragraphs']):
        for k in ['x','y','w','h']:assert abs(x[k]-y[k])<=1.5,(k,x,y)
def compare(b,w):
    size={'width':w,'height':844 if w<768 else 900}
    orig=b.new_page(viewport=size,java_script_enabled=False)
    p=b.new_page(viewport=size)
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
        go(orig,OLD);go(p,BASE)
        p.wait_for_function("document.querySelector('.pes-specialty').dataset.pesMotionState==='waiting'")
        old=geometry(orig); assert_same(old,geometry(p))
        scroll(p)
        p.wait_for_function("document.querySelector('.pes-specialty').dataset.pesMotionState==='playing'")
        for t in [0,140,350,650,1850]:
            if t: p.wait_for_timeout(t if t==140 else {350:210,650:300,1850:1200}[t])
            p.screenshot(path=str(OUT/f'pes-{w}-{t}.png'))
            assert abs(geometry(p)['section']['h']-old['section']['h'])<=1.5
        p.wait_for_function("!document.querySelector('.pes-motion-overlay')",timeout=5000)
        new=geometry(p); assert_same(old,new)
        assert new['headingCount']==1 and new['heading']['weight']=='300' and new['bold']['weight']=='700' and not new['overflow']
        assert 'Montserrat' in new['heading']['family']
        assert p.locator(SEL+' h2').inner_text().strip().replace('\n',' ')=='Precision behind the extraordinary.'
        assert p.locator(SEL+' a').get_attribute('href')=='about/'
        assert p.locator(SEL+' .pes-motion-rule').evaluate("e=>e.offsetHeight")==2
        assert p.locator(SEL).evaluate("e=>Array.from(e.querySelectorAll('p,a')).every(x=>getComputedStyle(x).opacity==='1')")
        scroll(orig);orig.screenshot(path=str(OUT/f'baseline-{w}.png'))
        p.evaluate("window.scrollTo({top:0,behavior:'instant'})");p.wait_for_timeout(100);scroll(p);p.wait_for_timeout(300)
        assert p.locator(SEL+' .am-char').count()==0
        p.locator(SEL+' a').focus();assert p.locator(SEL+' a').evaluate("e=>document.activeElement===e")
        assert p.locator(SEL+' a').evaluate("e=>getComputedStyle(e).opacity")== '1'
        assert not errors,errors
        results.append({'width':w,'baseline':old,'candidate':new,'pass':True})
    except Exception as e:
        failures.append({'width':w,'error':str(e)});p.screenshot(path=str(OUT/f'failure-{w}.png'));print('FAIL',w,e,flush=True)
    finally:orig.close();p.close()
def fallback(b,w,js,reduce):
    p=b.new_page(viewport={'width':w,'height':844},java_script_enabled=js,reduced_motion='reduce' if reduce else 'no-preference')
    try:
        go(p,BASE);scroll(p);p.wait_for_timeout(300)
        assert p.locator(SEL+' .am-char').count()==0
        assert p.locator(SEL+' [data-pending]').count()==0
        assert p.locator(SEL+' h2').evaluate("e=>getComputedStyle(e).opacity")=='1'
        assert p.locator(SEL+' a').is_visible()
        p.screenshot(path=str(OUT/f'fallback-{w}-{js}-{reduce}.png'))
        results.append({'fallback':[w,js,reduce],'pass':True})
    except Exception as e:failures.append({'fallback':[w,js,reduce],'error':str(e)})
    finally:p.close()
def reference(b,id,selector):
    p=b.new_page(viewport={'width':1440,'height':900})
    try:
        go(p,'https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id='+id)
        x=p.locator('#demo '+selector).first;x.wait_for(timeout=20000)
        if id=='ATZ-MOT-001':p.wait_for_function("document.querySelector('#demo [data-am-text]')?.hasAttribute('data-am-ready')")
        else:p.wait_for_function("document.querySelector('#demo [data-atz-id=ATZ-MOT-013]')?.dataset.tyReady==='true'")
        x.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-200,behavior:'instant'})")
        for t in [0,200,1200]:
            p.wait_for_timeout(t);p.screenshot(path=str(OUT/f'reference-{id}-{t}.png'))
        results.append({'reference':id,'pass':True})
    except Exception as e:failures.append({'reference':id,'error':str(e)});print('REFERENCE FAIL',id,e,flush=True)
    finally:p.close()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    reference(b,'ATZ-MOT-001','[data-am-text]')
    reference(b,'ATZ-MOT-013','[data-group]')
    for w in [375,390,768,1024,1440,1920]:compare(b,w)
    for w in [375,1440]:
        fallback(b,w,False,False);fallback(b,w,True,True)
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
print(json.dumps(failures),flush=True)
if failures:raise SystemExit(1)
