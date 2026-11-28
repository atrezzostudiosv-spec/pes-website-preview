from pathlib import Path
import subprocess, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
routes=["careers","careers/foreman","careers/journeyman","careers/electrician","careers/apprentice","contact"]
before={r:(ROOT/r/'index.html').read_bytes() for r in routes}
subprocess.run(['node','scripts/build_people_v4.mjs'],cwd=ROOT,check=True)
assert all((ROOT/r/'index.html').read_bytes()==before[r] for r in routes),'Generator drift'
OUT=ROOT/'people-v4-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch()
  for w,h,mode in [(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(390,844,'normal'),(375,812,'normal'),(390,844,'reduced'),(390,844,'no-js')]:
   for route in routes:
    page=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    assert page.goto(BASE+route+'/',wait_until='domcontentloaded').ok
    page.evaluate('document.fonts.ready')
    assert page.locator('main h1').count()==1
    assert page.locator('footer#pes-footer').count()==1
    assert page.locator('meta[name=robots]').get_attribute('content').startswith('noindex')
    for im in page.locator('main img').all():
     im.evaluate('e=>{e.loading="eager";return e.decode()}')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(route,w,mode)
    if route=='contact':
     assert page.locator('main form').count()==0
     assert page.locator('main fieldset[disabled]').count()==1
     assert page.locator('main fieldset :is(input,select,textarea,button):enabled').count()==0
     assert page.locator('main a[href="tel:+12135873257"]').count()>=1
    elif route=='careers':
     assert page.locator('main .pc4-roles a').count()==4
    else:
     assert 'Current vacancy and terms are not confirmed' in page.locator('main').inner_text()
    assert not errors,errors
    if w in (390,1440) and mode=='normal':
     for el in page.locator('main>section:visible').all():
      el.scroll_into_view_if_needed();page.wait_for_timeout(2000)
     page.evaluate('window.scrollTo(0,0)');page.wait_for_timeout(300)
     page.screenshot(path=str(OUT/f'{engine}-{w}-{route.replace("/","-")}.png'),full_page=True)
    results.append({'engine':engine,'width':w,'mode':mode,'route':route})
    page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0')
