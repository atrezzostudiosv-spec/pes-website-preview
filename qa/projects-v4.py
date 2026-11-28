import json, threading, subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'projects-v4-qa';OUT.mkdir(exist_ok=True)
routes=['portfolio','hillside','laurel-way','st-cloud']
before={r:(ROOT/r/'index.html').read_bytes() for r in routes}
subprocess.run(['node','scripts/build_projects_v4.mjs'],cwd=ROOT,check=True)
assert all((ROOT/r/'index.html').read_bytes()==before[r] for r in routes),'Generator drift'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch()
  for w,h,mode in [(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(390,844,'normal'),(375,812,'normal'),(1440,900,'reduced'),(390,844,'reduced'),(390,844,'no-js')]:
   for route in routes:
    for review in ([False,True] if mode!='no-js' else [False]):
     page=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
     errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
     assert page.goto(BASE+route+'/'+('?review=1' if review else ''),wait_until='domcontentloaded',timeout=45000).ok
     page.evaluate('document.fonts.ready')
     if review:page.wait_for_function("document.body.classList.contains('pv4-review')")
     assert page.locator('main h1').count()==1
     assert page.locator('footer#pes-footer').count()==1
     assert page.locator('meta[name=robots]').get_attribute('content').startswith('noindex')
     for im in page.locator('main img').all():
      if im.is_visible():im.evaluate('e=>{e.loading="eager";return e.decode()}')
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(route,w,mode,review)
     if route!='portfolio':
      chapters=page.locator('[data-pv4-chapter]')
      assert chapters.count()==8
      if review:assert all(x.is_visible() for x in chapters.all()),(route,w)
      else:assert not any(x.is_visible() for x in page.locator('[data-review-only]').all())
      assert page.locator('main a[href*="contact/"]').count()==1
     if route=='hillside':
      assert page.locator('.pv4-gallery-item').count()==7
      if mode=='normal':
       img=page.locator('.pv4-parallax-frame img');img.wait_for()
       page.locator('.pv4-parallax-frame').scroll_into_view_if_needed()
       page.wait_for_timeout(250)
       a=img.evaluate("e=>e.style.getPropertyValue('--am-y')")
       page.evaluate("window.scrollBy(0,250)");page.wait_for_timeout(250)
       z=img.evaluate("e=>e.style.getPropertyValue('--am-y')")
       assert a and z and a!=z,(a,z)
       page.evaluate("window.scrollBy(0,-250)");page.wait_for_timeout(250)
       assert abs(float(img.evaluate("e=>e.style.getPropertyValue('--am-y')").replace('px',''))-float(a.replace('px','')))<2
      else:assert page.locator('.pv4-parallax-frame').count()==0
     if route=='st-cloud':assert page.locator('.pv4-hero>img').count()==0
     assert not errors,errors
     if w in (1440,390) and mode=='normal' and review:
      for el in page.locator('main>section:visible').all():
       el.scroll_into_view_if_needed();page.wait_for_timeout(2200)
      page.evaluate('window.scrollTo(0,0)');page.wait_for_timeout(250)
      page.screenshot(path=str(OUT/f'{engine}-{w}-{route}-review.png'),full_page=True)
     results.append({'engine':engine,'viewport':[w,h],'mode':mode,'route':route,'review':review})
     page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0')
