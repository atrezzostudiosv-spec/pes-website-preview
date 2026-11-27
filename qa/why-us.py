import json, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'why-us-qa'; OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
SECTIONS=['why-us-hero','why-us-mission','why-us-expertise','why-us-relationships','why-us-people','why-us-connect']
results=[]
with sync_playwright() as p:
 for engine in ('chromium','webkit'):
  b=getattr(p,engine).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(375,812,'normal'),(390,844,'normal'),(390,844,'reduced'),(1440,900,'reduced'),(1440,900,'no-js'),(320,667,'normal')]:
   page=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(BASE+'about/',wait_until='domcontentloaded',timeout=45000).ok
   page.evaluate('document.fonts.ready')
   assert page.locator('main h1').count()==1
   assert page.locator('footer#pes-footer').count()==1
   assert page.locator('main').inner_text().find('Established in 2007')>=0
   assert 'PES is licensed, bonded and insured.' in page.locator('main').inner_text()
   assert page.locator('.pes-why-values li').count()==5
   for route in ['portfolio/','capabilities/','careers/','contact/']:
    assert page.locator(f'main a[href="../{route}"]').count()>=1
   for section in SECTIONS:
    s=page.locator('#'+section)
    s.locator('h1,h2').first.scroll_into_view_if_needed()
    if mode=='normal':page.wait_for_timeout(1900)
    for im in s.locator('img').all():
     im.evaluate('e=>{e.loading="eager";return e.decode()}')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(section,w)
    for heading in s.locator('h1,h2,h3').all():
     data=heading.evaluate("""e=>{const r=e.getBoundingClientRect(),s=e.querySelector('strong');return {light:getComputedStyle(e).fontWeight,bold:s?getComputedStyle(s).fontWeight:null,left:r.left,right:r.right,scroll:e.scrollWidth,width:e.clientWidth}}""")
     assert data['light']=='300' and data['bold']=='700',data
     assert data['left']>=-1 and data['right']<=w+1 and data['scroll']<=data['width']+1,(section,w,data)
    if w in (1440,390) and mode=='normal':page.screenshot(path=str(OUT/f'{engine}-{w}-{section}.png'))
    results.append({'engine':engine,'viewport':[w,h],'mode':mode,'section':section})
   journey=page.locator('[data-am-journey]')
   if w>=1101 and mode=='normal':
    assert journey.get_attribute('data-am-ready') is not None
    for i in (0,1,0):
     journey.locator('[data-am-journey-step]').nth(i).evaluate("e=>window.scrollTo(0,scrollY+e.getBoundingClientRect().top-innerHeight*.4)")
     page.wait_for_timeout(650)
     assert journey.locator('[data-am-journey-counter]').inner_text()==f'{i+1:02d}'
   else:
    assert journey.locator('.am-journey__sticky').evaluate("e=>getComputedStyle(e).display")=='none'
    assert all(im.is_visible() for im in journey.locator('.am-step-image img').all())
   page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
