import json,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'home-close-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/';results=[]
with sync_playwright() as p:
 for name in ['chromium','webkit']:
  b=getattr(p,name).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(390,844,'normal'),(375,812,'normal'),(390,844,'reduced'),(390,844,'no-js'),(844,390,'normal')]:
   page=b.new_page(viewport={'width':w,'height':h},has_touch=w<768,is_mobile=w<768,reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(url,wait_until='load',timeout=45000).ok
   scene=page.locator('#pes-connect');footer=page.locator('#pes-footer')
   assert page.locator('#pes-featured-brands + #pes-connect').count()==1
   assert footer.locator('nav a').count()==6 and footer.locator('.logo').get_attribute('src')=='assets/brand/pes-logo-flat.svg'
   assert scene.locator('img').get_attribute('src')=='assets/media/pes-connect-los-angeles.webp'
   assert scene.locator('img').evaluate("async e=>{await e.decode();return e.naturalWidth===2048&&e.naturalHeight===1366}"),'New contact image did not decode at expected dimensions'
   assert scene.locator('a.button').get_attribute('href')=='contact/'
   assert scene.locator('a.phone').get_attribute('href')=='tel:+12135873257'
   assert footer.evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(0, 0, 0)'
   assert footer.locator('.pes-footer-light').evaluate("e=>e.offsetHeight")==2
   if mode=='normal' and h>=600:
    page.wait_for_function("document.querySelector('#pes-connect').classList.contains('is-pes-connect-active')")
    page.evaluate('document.fonts.ready')
    page.wait_for_function("window.ScrollTrigger && ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))")
    scene.locator('img').evaluate("e=>e.decode()")
    states=[]
    for q in [0,.5,.99,.25]:
     scene.evaluate("(e,q)=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-e.querySelector('.pes-connect-stage').offsetHeight)*q,behavior:'instant'})",q)
     page.wait_for_timeout(250)
     data=scene.evaluate("""e=>({p:+e.dataset.pesConnectProgress,scale:+e.style.getPropertyValue('--pes-connect-scale'),top:e.querySelector('.pes-connect-stage').getBoundingClientRect().top,copyTop:e.querySelector('.pes-connect-content').getBoundingClientRect().top,travel:e.offsetHeight-e.querySelector('.pes-connect-stage').offsetHeight})""")
     assert abs(data['p']-q)<.025 and abs(data['top'])<4,data
     assert abs(data['scale']-(1+(.16 if w<=820 else .24)*q))<.01,data
     assert data['travel']>h*.55,data
     states.append(data)
     if q in [0,.99]:page.screenshot(path=str(OUT/f'{name}-{w}-{q}.png'))
    assert max(d['copyTop'] for d in states)-min(d['copyTop'] for d in states)<5,states
   else:
    assert scene.locator('.pes-connect-stage').evaluate("e=>getComputedStyle(e).position")=='relative'
    assert scene.locator('img').evaluate("e=>getComputedStyle(e).transform") in ['none','matrix(1, 0, 0, 1, 0, 0)']
    states=[]
   footer.scroll_into_view_if_needed();page.wait_for_timeout(2100)
   assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
   page.screenshot(path=str(OUT/f'{name}-{w}-{mode}-footer.png'))
   results.append({'browser':name,'width':w,'height':h,'mode':mode,'states':states})
   page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2));print('TOTAL',len(results),'FAILURES 0',flush=True)
