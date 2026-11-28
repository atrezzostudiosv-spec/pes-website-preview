"""Regression: match every animated glyph to its native text range before handoff."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'title-glyph-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
Thread(target=s.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{s.server_port}/'
CASES=[('','.pes-specialty h2'),('about/','[data-pes-editorial] h1'),('capabilities/','.sv4-hero h1'),('capabilities/power-quality-and-energy-management/','.sv4-hero h1'),('hillside/','.pv4-hero h1'),('careers/','.pc4-hero h1'),('contact/','.pc4-hero h1')]
GEOMETRY=r"""h=>{
 const source=h.querySelector('.pes-global-title-source,.pes-motion-source'),overlay=h.querySelector('[data-pes-glyph-aligned]');
 const chars=[...overlay.querySelectorAll('.am-char')];
 const rangeRects=root=>{let w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),n,res=[];while(n=w.nextNode()){let o=0;for(const ch of n.data){let a=o;o+=ch.length;if(/\s/u.test(ch))continue;let r=document.createRange();r.setStart(n,a);r.setEnd(n,o);let q=r.getBoundingClientRect();res.push([q.left,q.top]);}}return res;};
 const original=rangeRects(source);
 const old=chars.map(c=>[c.style.getPropertyValue('transform'),c.style.getPropertyPriority('transform'),c.style.getPropertyValue('transition'),c.style.getPropertyPriority('transition')]);
 chars.forEach(c=>{c.style.setProperty('transition','none','important');c.style.setProperty('transform','none','important');});
 const visual=chars.map(c=>rangeRects(c)[0]);
 let max=0;visual.forEach((p,i)=>{max=Math.max(max,Math.abs(p[0]-original[i][0]),Math.abs(p[1]-original[i][1]));});
 chars.forEach((c,i)=>{for(const [k,j] of [['transform',0],['transition',2]]){if(old[i][j])c.style.setProperty(k,old[i][j],old[i][j+1]);else c.style.removeProperty(k);}});
 return {max,count:chars.length,source:original.length};
}"""
results=[]
with sync_playwright() as pw:
 for engine in ['chromium','webkit']:
  b=getattr(pw,engine).launch()
  for width in [375,390,768,1440]:
   for route,selector in CASES:
    page=b.new_page(viewport={'width':width,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    assert page.goto(BASE+route,wait_until='domcontentloaded').ok
    page.evaluate('document.fonts.ready')
    h=page.locator(selector).first
    h.scroll_into_view_if_needed()
    h.locator('[data-pes-glyph-aligned]').wait_for(state='attached',timeout=5000)
    geo=h.evaluate(GEOMETRY)
    assert geo['count']==geo['source'] and geo['max']<=1,(route,width,engine,geo)
    h.locator('[data-pes-glyph-aligned]').wait_for(state='detached',timeout=5000)
    assert h.locator('.am-char').count()==0
    assert not errors,errors
    results.append({'route':route,'width':width,'engine':engine,**geo})
    page.close()
  page=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
  page.goto(BASE+'careers/',wait_until='domcontentloaded');page.evaluate('document.fonts.ready')
  assert page.locator('[data-pes-glyph-aligned]').count()==0
  page.close();b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0')
