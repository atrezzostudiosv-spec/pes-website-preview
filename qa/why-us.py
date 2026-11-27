import json, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'why-us-qa'; OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
results=[]
with sync_playwright() as p:
 for engine in ('chromium','webkit'):
  b=getattr(p,engine).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(375,812,'normal'),(390,844,'normal'),(390,844,'reduced'),(390,844,'no-js'),(320,667,'normal')]:
   page=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(BASE+'about/',wait_until='domcontentloaded',timeout=45000).ok
   page.evaluate('document.fonts.ready')
   assert page.locator('main h1').count()==1
   assert page.locator('main .review-note').count()==0
   assert page.locator('header .brand .logo-light').get_attribute('src')=='../assets/brand/pes-logo-flat.svg'
   assert page.locator('footer#pes-footer .pes-footer-light').count()==1
   assert page.locator('#why-us-hero .pes-about-link').evaluate('e=>e.href')==BASE+'contact/'
   assert page.locator('#why-us-expertise .pes-about-link').evaluate('e=>e.href')==BASE+'capabilities/'
   assert page.locator('#why-us-connect .phone').get_attribute('href')=='tel:+12135873257'
   for section in ['why-us-hero','why-us-approach','why-us-expertise','why-us-connect']:
    s=page.locator('#'+section)
    s.locator('h1,h2').scroll_into_view_if_needed()
    if mode=='normal':
     page.wait_for_function("id=>document.querySelector('#'+id).dataset.pesEditorialReady==='true'",arg=section)
     page.wait_for_timeout(2200)
    for im in s.locator('img').all():
     im.evaluate('e=>{e.loading="eager";return e.decode()}')
    heading=s.locator('h1,h2')
    data=heading.evaluate("""e=>{const r=e.getBoundingClientRect(),s=e.querySelector('strong');return {light:getComputedStyle(e).fontWeight,bold:getComputedStyle(s).fontWeight,left:r.left,right:r.right,scroll:e.scrollWidth,width:e.clientWidth}}""")
    assert data['light']=='300' and data['bold']=='700',data
    assert data['left']>=-1 and data['right']<=w+1 and data['scroll']<=data['width']+1,(section,w,data)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(section,w)
    if w in (1440,390) and mode=='normal':page.screenshot(path=str(OUT/f'{engine}-{w}-{section}.png'))
    results.append({'engine':engine,'viewport':[w,h],'mode':mode,'section':section,**data})
   page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
