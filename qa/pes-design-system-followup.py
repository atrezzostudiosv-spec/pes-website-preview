import json,threading,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa-followup';OUT.mkdir(exist_ok=True)
BASELINE=ROOT.parent/'pes-before-design'
subprocess.run(['git','worktree','add','--detach',str(BASELINE),'230937de2990bae0e33c040d96c4dee071dc3fcf'],cwd=ROOT,check=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def serve(directory):
    s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(directory),**kw))
    threading.Thread(target=s.serve_forever,daemon=True).start()
    return f'http://127.0.0.1:{s.server_port}/'
LOCAL=serve(ROOT);OLD=serve(BASELINE)
LIVE='https://atrezzostudiosv-spec.github.io/pes-website-preview/'
DEMO='https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/components/originales/atrezzo/ATZ-SEC-016/index.html'
results=[];failures=[]
def open_page(b,url,w):
    p=b.new_page(viewport={'width':w,'height':844 if w<768 else 900},device_scale_factor=1)
    p.goto(url,wait_until='domcontentloaded',timeout=30000);p.evaluate('document.fonts.ready');p.wait_for_timeout(400);return p
def capture(p,name):p.screenshot(path=str(OUT/(name+'.png')))
def safe(name,fn):
    try:results.append({'name':name,'status':'passed','metrics':fn()})
    except Exception as e:failures.append(f'{name}: {e}');results.append({'name':name,'status':'failed','error':str(e)})
def menu(b,kind,url,w):
    p=open_page(b,url,w)
    try:
        p.locator('[data-open="menu-dialog"]').click();p.wait_for_timeout(600)
        assert p.locator('#menu-dialog').evaluate('(e)=>e.open')
        capture(p,f'{kind}-{w}-menu-settled')
        p.locator('.menu-group summary').first.click();p.wait_for_timeout(250)
        capture(p,f'{kind}-{w}-submenu-settled')
        v=p.locator('#menu-dialog').evaluate("(e)=>({opacity:getComputedStyle(e).opacity,background:getComputedStyle(e).backgroundColor,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight})")
        assert v['opacity']=='1',v
        p.keyboard.press('Escape');assert not p.locator('#menu-dialog').evaluate('(e)=>e.open')
        return v
    finally:p.close()
def live(b):
    p=open_page(b,LIVE+'?ds=2d470ed',1440)
    try:
        p.wait_for_function("document.querySelector('.site-header .logo-light')?.naturalWidth===720",timeout=10000)
        assert p.locator('body').evaluate("(e)=>e.classList.contains('pes-site') && getComputedStyle(e).fontFamily.includes('Montserrat')")
        capture(p,'live-1440-top');p.evaluate("scrollTo({top:66,behavior:'instant'})");p.wait_for_timeout(650);capture(p,'live-1440-glass')
        p.evaluate("scrollTo({top:0,behavior:'instant'})");p.wait_for_timeout(650)
        p.locator('.site-header details[data-header-nav] summary').hover();p.wait_for_timeout(350);capture(p,'live-1440-dropdown')
        return {'url':p.url,'logo':p.locator('.site-header .logo-light').get_attribute('src')}
    finally:p.close()
def motion(b,route,w):
    records=[]
    for kind,base in [('before',OLD),('after',LOCAL)]:
        p=open_page(b,base+route,w)
        try:
            root=p.locator('[data-atz-id]').first
            assert root.count(),route
            id=root.get_attribute('data-atz-id');bounds=root.evaluate('(e)=>({top:e.getBoundingClientRect().top+scrollY,height:e.getBoundingClientRect().height})')
            for fraction in [0.05,0.35,0.65,0.9]:
                p.evaluate("(y)=>scrollTo({top:y,behavior:'instant'})",bounds['top']+max(0,bounds['height']-900)*fraction)
                p.wait_for_timeout(350)
                capture(p,f'{kind}-{id}-{w}-{int(fraction*100)}')
            rec={'kind':kind,'id':id,'height':bounds['height'],'overflow':p.evaluate('document.documentElement.scrollWidth>innerWidth')}
            records.append(rec)
        finally:p.close()
    assert records[0]['id']==records[1]['id']
    assert not records[1]['overflow'],records
    return records
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--autoplay-policy=no-user-gesture-required'])
    for w in [375,1024]:
        safe(f'demo menu {w}',lambda w=w:menu(b,'reference',DEMO,w))
        safe(f'PES menu {w}',lambda w=w:menu(b,'pes',LOCAL,w))
    safe('live Pages preview',lambda:live(b))
    for route in ['', 'capabilities/','capabilities/lighting-design/']:
        for w in [375,1440]:
            safe(f'motion {route or "home"} {w}',lambda route=route,w=w:motion(b,route,w))
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
print(json.dumps({'results':results,'failures':failures},indent=2),flush=True)
if failures:raise SystemExit(1)

# Verify final font-family override on the actual split scene.
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    for url in [LOCAL+'capabilities/lighting-design/', LIVE+'capabilities/lighting-design/?ds=2d470ed']:
        page=open_page(b,url,1440)
        nodes=page.locator('.ss03__text')
        assert nodes.count()>0
        assert all('Montserrat' in x for x in nodes.evaluate_all('(nodes)=>nodes.map(e=>getComputedStyle(e).fontFamily)'))
        page.close()
    b.close()
print("Final split scene Montserrat family verified.",flush=True)
