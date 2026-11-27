import json, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'light-as-motion-qa'; OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/'
SCENES=[
 ('hillside','#pes-featured-project','.ats-stage','.ats-split-image','::before'),
 ('services','#pes-services [data-collection-track]','.collection-stage','.collection-image-wrap','::after'),
 ('difference','#ats2-handoff','.ats2-stage','.ats2-handoff-pane','::before')]
results=[]
def position(page,track,kind):
 track.evaluate("""(e,k)=>{const r=e.getBoundingClientRect(), h=innerHeight, y=scrollY;
 const top=r.top+y, bottom=r.bottom+y;
 const target=k==='entry'?top-.92*h:k==='approach'?top-.65*h:k==='arrival'?top:k==='reveal'?top+.16*h:k==='middle'?(top+Math.max(0,r.height-h)*.5):bottom-.52*h;
 window.scrollTo({top:target,behavior:'instant'});}""",kind)
 page.wait_for_timeout(150)
def state(stage):
 return stage.evaluate("""e=>({entry:+e.style.getPropertyValue('--pes-light-in'),exit:+e.style.getPropertyValue('--pes-light-out'),top:e.getBoundingClientRect().top})""")
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  browser=getattr(p,engine).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(375,812,'normal'),(390,844,'normal'),(390,844,'reduced'),(390,844,'no-js'),(844,390,'normal')]:
   page=browser.new_page(viewport={'width':w,'height':h},has_touch=w<768,is_mobile=w<768,reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(URL,wait_until='load',timeout=45000).ok
   if mode=='normal' and h>=600:
    page.evaluate('document.fonts.ready')
    page.wait_for_function("window.ScrollTrigger && ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))")
    page.wait_for_function("document.querySelectorAll('[data-pes-light-ready]').length===3")
    for name,track_sel,stage_sel,photo_sel,pseudo in SCENES:
     track=page.locator(track_sel);stage=track.locator(stage_sel)
     assert stage.locator(photo_sel).first.evaluate("(e,p)=>getComputedStyle(e,p).pointerEvents",pseudo)=='none'
     states={}
     phases=['entry','approach','arrival','reveal','middle','exit','middle','reveal','arrival','approach','entry'] if name!='hillside' else ['entry','middle','exit','middle','entry']
     for phase in phases:
      position(page,track,phase)
      data=state(stage); states.setdefault(phase,[]).append(data)
      if phase=='entry':assert data['entry']>.85 and data['exit']<.05,(name,phase,data)
      elif phase in ['approach','arrival']:assert data['entry']>.99 and data['exit']<.05,(name,phase,data)
      elif phase=='reveal':assert .25<data['entry']<.75 and data['exit']<.05 and abs(data['top'])<5,(name,phase,data)
      elif phase=='middle':assert data['entry']<.02 and data['exit']<.02 and abs(data['top'])<5,(name,phase,data)
      else:assert data['exit']>.65 and data['entry']<.05,(name,phase,data)
      if w in [1440,390] and len(states[phase])==1:
       page.screenshot(path=str(OUT/f'{engine}-{w}-{name}-{phase}.png'))
     assert abs(states['middle'][0]['entry']-states['middle'][1]['entry'])<.02
     assert abs(states['entry'][0]['entry']-states['entry'][1]['entry'])<.02
     results.append({'engine':engine,'viewport':[w,h],'scene':name,'states':states})
   else:
    assert page.locator('[data-pes-light-ready]').count()==0
    results.append({'engine':engine,'viewport':[w,h],'mode':mode,'static':True})
   assert page.locator('.pes-cinematic-interlude [data-pes-light-ready]').count()==0
   assert page.locator('#pes-featured-project .pes-split-link').get_attribute('href')=='hillside/'
   assert page.locator('#pes-services [data-collection-tab]').count()==5
   assert page.locator('#pes-connect [data-pes-light-ready]').count()==0
   fade=page.locator('#pes-connect .pes-connect-shade').evaluate("e=>getComputedStyle(e).getPropertyValue('--pes-connect-top-fade').trim()")
   assert fade.startswith('linear-gradient(180deg,#000 0%') and fade.endswith('transparent 52%)'),fade
   if mode=='normal' and h>=600:
    connect=page.locator('#pes-connect')
    for phase in ['approach','arrival','middle']:
     position(page,connect,phase)
     assert page.locator('#pes-connect .pes-connect-shade').evaluate("e=>getComputedStyle(e).getPropertyValue('--pes-connect-top-fade').trim()")==fade
   assert page.locator('#pes-connect .button').get_attribute('href')=='contact/'
   assert page.locator('#pes-connect .phone').get_attribute('href')=='tel:+12135873257'
   assert page.locator('#pes-footer .pes-footer-light').evaluate("e=>e.offsetHeight")==2
   assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
   page.close()
  browser.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
