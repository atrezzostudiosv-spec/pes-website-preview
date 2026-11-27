import hashlib,json,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'handoff-reading-qa';OUT.mkdir(exist_ok=True)
def blob(path):
 b=path.read_bytes();return hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()
assert blob(ROOT/'assets/vendor/ats2-engine.js')=='dbc50858a0e026a0941587b1885a99eaa6ab2111'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/';results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(375,812,'normal'),(390,844,'normal'),(844,390,'normal'),(390,844,'reduced'),(390,844,'no-js')]:
   page=b.new_page(viewport={'width':w,'height':h},has_touch=w<768,is_mobile=w<768,reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(URL,wait_until='load',timeout=45000).ok
   scene=page.locator('#ats2-handoff');stage=scene.locator('.ats2-stage')
   assert scene.locator('.ats2-handoff-pane').count()==2
   assert scene.locator('.ats2-handoff-copy h2').all_text_contents()==['Precision.Built in.','Light.Considered.']
   await_fonts=page.evaluate("document.fonts.ready.then(()=>true)")
   assert scene.locator('.ats2-handoff-copy h2 strong').all_text_contents()==['Built in.','Considered.']
   typography=scene.locator('.ats2-handoff-copy h2').evaluate_all("""es=>es.map(e=>{const s=e.querySelector('strong'),a=getComputedStyle(e),b=getComputedStyle(s),r=s.getBoundingClientRect(),c=e.closest('.ats2-handoff-copy').getBoundingClientRect();return {first:a.fontWeight,second:b.fontWeight,font:a.fontFamily,right:r.right,limit:c.right}})""")
   assert all(x['first']=='300' and x['second']=='700' and 'Montserrat' in x['font'] for x in typography),typography
   if mode=='normal':
    page.wait_for_function("document.querySelector('#ats2-handoff').closest('.ats2-scope').classList.contains('ats2-enhanced')")
    page.evaluate('document.fonts.ready')
    page.wait_for_function("window.ScrollTrigger && ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))")
    states=[]
    for q in [0,.15,.30,.50,.70,.85,.99,.85,.50,.30,.15]:
     scene.evaluate("""(e,q)=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*q,behavior:'instant'})""",q)
     page.wait_for_function("""q=>Math.abs(Number(document.querySelector('#ats2-handoff').dataset.ats2Progress)-q)<.025""",arg=q)
     data=scene.evaluate("""e=>{const s=e.querySelector('.ats2-stage').getBoundingClientRect();return {p:+e.dataset.ats2Progress,wipe:parseFloat(e.style.getPropertyValue('--ats2-wipe')),first:+e.style.getPropertyValue('--ats2-first-copy'),second:+e.style.getPropertyValue('--ats2-second-copy'),top:s.top,travel:e.offsetHeight-s.height,h:s.height}}""")
     assert abs(data['top'])<5 and abs(data['travel']/data['h']-3.4)<.05,(w,h,q,data)
     if q<=.30:assert data['first']>.99 and data['wipe']>99.9 and data['second']<.01,(w,h,q,data)
     if q==.50:assert 0<data['wipe']<100 and max(data['first'],data['second'])<.01,(w,h,q,data)
     if q>=.70:assert data['second']>.99 and data['wipe']<.01 and data['first']<.01,(w,h,q,data)
     states.append({'q':q,**data})
     if w in [1440,390] and q in [.15,.50,.85]:page.screenshot(path=str(OUT/f'{engine}-{w}-{q}.png'))
    results.append({'engine':engine,'viewport':[w,h],'states':states})
   else:
    assert not scene.evaluate("e=>e.closest('.ats2-scope').classList.contains('ats2-enhanced')")
    assert stage.evaluate("e=>getComputedStyle(e).position")=='relative'
    results.append({'engine':engine,'viewport':[w,h],'mode':mode,'static':True})
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
