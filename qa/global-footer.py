import json, threading
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'global-footer-qa'; OUT.mkdir(exist_ok=True)
PAGES=sorted(p for p in ROOT.rglob('index.html') if not any(x in ('assets','.git') for x in p.relative_to(ROOT).parts))
assert len(PAGES)==16
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a): pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
DEST=['','about/','portfolio/','capabilities/','careers/','contact/']
results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(375,812,'normal'),(390,844,'normal'),(390,844,'reduced'),(390,844,'no-js')]:
   # Test all pages at one desktop and one mobile size; sample the remaining widths.
   paths=PAGES if (w,h,mode) in [(1440,900,'normal'),(390,844,'normal')] else [ROOT/'index.html',ROOT/'about/index.html',ROOT/'capabilities/lighting-design/index.html']
   for path in paths:
    route=path.relative_to(ROOT).as_posix().removesuffix('index.html')
    page=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
    url=BASE+route
    assert page.goto(url,wait_until='domcontentloaded',timeout=45000).ok
    foot=page.locator('footer#pes-footer'); assert foot.count()==1
    assert page.locator('#pes-connect').count()==(1 if not route else 0)
    assert foot.locator('.pes-footer-nav a').all_text_contents()==['Home','Why Us','Projects','Services','Careers','Contact']
    links=foot.locator('.pes-footer-nav a').evaluate_all('es=>es.map(e=>e.href)')
    assert links==[BASE+d for d in DEST],(route,links)
    assert foot.locator('.pes-footer-nav a[aria-current=page]').count()==int(route in DEST)
    assert foot.locator('.pes-footer-contact a').evaluate_all('es=>es.map(e=>e.getAttribute("href"))')==['tel:+12135873257','https://www.instagram.com/pes.la/']
    logo=foot.locator('img.logo'); assert logo.evaluate('e=>e.src')==BASE+'assets/brand/pes-logo-flat.svg'
    logo.evaluate('e=>{e.loading="eager";return e.decode()}')
    page.evaluate('document.fonts.ready')
    foot.locator('.pes-footer-light').scroll_into_view_if_needed()
    data=foot.evaluate("""e=>{const g=e.querySelector('.pes-footer-grid'),l=e.querySelector('.pes-footer-light'),r=e.getBoundingClientRect();return {bg:getComputedStyle(e).backgroundColor,columns:getComputedStyle(g).gridTemplateColumns,light:getComputedStyle(l).backgroundColor,lightHeight:l.offsetHeight,left:r.left,right:r.right,overflow:document.documentElement.scrollWidth>innerWidth+1}}""")
    assert data['bg']=='rgb(0, 0, 0)' and data['light']=='rgb(162, 253, 2)' and data['lightHeight']==2 and not data['overflow'],(route,w,data)
    assert len(data['columns'].split())==(2 if w<=820 else 3),(route,w,data)
    if mode=='normal':
     page.wait_for_function("document.querySelector('#pes-footer').classList.contains('is-neon-lit')")
     assert foot.locator('.pes-footer-light').evaluate("e=>getComputedStyle(e,'::after').animationName")=='pesNeonTravel'
    else:
     assert foot.locator('.pes-footer-light').evaluate("e=>getComputedStyle(e,'::after').animationName")=='none'
    if path in [ROOT/'index.html',ROOT/'about/index.html',ROOT/'capabilities/lighting-design/index.html'] and w in (1440,390):
     foot.screenshot(path=str(OUT/f'{engine}-{w}-{mode}-{route.replace("/","-") or "home"}.png'))
    results.append({'engine':engine,'viewport':[w,h],'mode':mode,'route':route,**data})
    page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
