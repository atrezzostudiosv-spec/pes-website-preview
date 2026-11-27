import json,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'featured-brands-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
results=[]
with sync_playwright() as p:
 for name in ['chromium','webkit']:
  b=getattr(p,name).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(390,844,'normal'),(375,812,'normal'),(390,844,'reduced'),(390,844,'no-js')]:
   page=b.new_page(viewport={'width':w,'height':h},has_touch=w<768,is_mobile=w<768,reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(url,wait_until='load',timeout=45000).ok
   section=page.locator('#pes-featured-brands');grid=section.locator('[data-group]')
   assert section.get_by_role('heading',name='Featured Brands').count()==1
   assert section.locator('[role=img]').count()==6
   data=section.evaluate("""e=>({color:getComputedStyle(e).backgroundColor,weight:getComputedStyle(e.querySelector('h2')).fontWeight,titleColor:getComputedStyle(e.querySelector('h2')).color,columns:getComputedStyle(e.querySelector('ul')).gridTemplateColumns.split(' ').length,marks:[...e.querySelectorAll('.pes-brand-mark')].map(x=>({w:x.offsetWidth,h:x.offsetHeight,pos:getComputedStyle(x).backgroundPosition,filter:getComputedStyle(x).filter})),next:e.nextElementSibling.matches('.ui.close.dark'),previous:e.previousElementSibling.querySelector('#ats2-handoff')!==null})""")
   assert data['color']=='rgb(0, 0, 0)' and data['titleColor']=='rgb(255, 255, 255)' and data['weight']=='300'
   assert data['columns']==(3 if w<768 else 6) and data['next'] and data['previous'],data
   assert all(0<m['w']<=156 and m['h']>0 for m in data['marks'])
   assert len(set(m['pos'] for m in data['marks']))==6
   assert all('grayscale(1)' in m['filter'] and 'invert(1)' in m['filter'] for m in data['marks'])
   assert page.evaluate("""async()=>{let i=new Image();i.src='assets/brand/pes-featured-brands-preview.webp';await i.decode();return i.naturalWidth===180&&i.naturalHeight===492}""")
   if mode=='normal':
    page.wait_for_function("document.querySelector('#pes-featured-brands').dataset.tyReady==='true'")
    delays=grid.evaluate("e=>[...e.children].map(x=>x.getAnimations()[0]?.effect.getTiming().delay)")
    assert delays==[0,120,240,360,480,600],delays
   section.scroll_into_view_if_needed();page.wait_for_timeout(1650)
   assert grid.evaluate("e=>[...e.children].every(x=>Number(getComputedStyle(x).opacity)>.99)")
   assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
   page.screenshot(path=str(OUT/f'{name}-{w}-{mode}.png'))
   shade=page.locator('#pes-connect .pes-connect-shade')
   fade=shade.evaluate("e=>getComputedStyle(e).getPropertyValue('--pes-connect-top-fade').trim()")
   assert shade.locator('..').get_attribute('data-pes-light-ready') is None
   assert fade.startswith('linear-gradient(180deg,#000 0%') and fade.endswith('transparent 52%)'),fade
   layers=shade.evaluate("e=>getComputedStyle(e).backgroundImage")
   assert layers.count('linear-gradient(')==3 and '52%' in layers.split('), linear-gradient(')[0],layers
   padding=section.evaluate("e=>parseFloat(getComputedStyle(e).paddingBottom)")
   assert abs(padding-(72 if w<768 else min(120,max(78,w*.075))))<1,(w,padding)
   assert section.evaluate("e=>Math.abs(e.getBoundingClientRect().bottom-e.nextElementSibling.getBoundingClientRect().top)<2")
   if mode!='no-js':
    page.locator('#pes-connect img').evaluate('e=>e.decode()')
    page.locator('#pes-connect').evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-innerHeight*.42,behavior:'instant'})")
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT/f'{name}-{w}-{mode}-seam.png'))
   results.append({'browser':name,'width':w,'mode':mode,**data})
   page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
