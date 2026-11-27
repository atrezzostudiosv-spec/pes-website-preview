import json,threading,hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hillside-mobile-qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
results=[]
source=(ROOT/'assets/vendor/ats1-engine.js').read_bytes()
assert hashlib.sha1(('blob '+str(len(source))+'\0').encode()+source).hexdigest()=='3022616065b5101710865b66673f439216d97560'
def check(browser,name,w,h,mobile,reduced=False):
    page=browser.new_page(viewport={'width':w,'height':h},has_touch=mobile,is_mobile=mobile,reduced_motion='reduce' if reduced else 'no-preference')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
        assert page.goto(url,wait_until='load',timeout=45000).ok
        page.evaluate('document.fonts.ready')
        page.wait_for_function("window.ScrollTrigger && document.querySelector('.pes-featured-split') && ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))" if not reduced else "document.querySelector('.pes-featured-split')")
        scene=page.locator('#pes-featured-project')
        copy=scene.locator('.ats-split-copy')
        duration=copy.evaluate("e=>getComputedStyle(e).transitionDuration")
        if mobile and not reduced:
            assert '0.62s' in duration,duration
            scene.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY,behavior:'instant'})")
            page.wait_for_timeout(800)
            assert float(copy.evaluate("e=>getComputedStyle(e).opacity"))<.02
            scene.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*.36,behavior:'instant'})")
            page.wait_for_function("Number(document.querySelector('#pes-featured-project').style.getPropertyValue('--ats-copy-alpha'))>.95")
            a=float(copy.evaluate("e=>getComputedStyle(e).opacity"))
            page.wait_for_timeout(220)
            b=float(copy.evaluate("e=>getComputedStyle(e).opacity"))
            page.wait_for_timeout(650)
            c=float(copy.evaluate("e=>getComputedStyle(e).opacity"))
            assert 0<=a<b<.99 and c>.99,(a,b,c)
            page.screenshot(path=str(OUT/f'{name}-{w}-end.png'))
            hold=[]
            for q in [.36,.55,.75,.95,.42]:
                scene.evaluate("(e,q)=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*q,behavior:'instant'})",q)
                page.wait_for_timeout(750)
                state=scene.evaluate("""e=>{const s=e.querySelector('.ats-stage').getBoundingClientRect(),c=e.querySelector('.ats-split-copy');return {p:+e.dataset.atsProgress,alpha:+getComputedStyle(c).opacity,top:s.top,travel:e.offsetHeight-innerHeight,clip:parseFloat(e.style.getPropertyValue('--ats-image-clip'))}}""")
                assert abs(state['p']-q)<.005 and state['alpha']>.99 and abs(state['top'])<3,state
                assert state['travel']*.64>=h*1.50 and state['clip']>41.9,state
                hold.append(state)
            # A rapid 1-viewport native scroll step from the complete frame
            # must still leave the scene pinned and fully legible.
            scene.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*.36+innerHeight,behavior:'instant'})")
            page.wait_for_timeout(750)
            fast=scene.evaluate("""e=>({p:+e.dataset.atsProgress,alpha:+getComputedStyle(e.querySelector('.ats-split-copy')).opacity,top:e.querySelector('.ats-stage').getBoundingClientRect().top})""")
            assert fast['p']<.99 and fast['alpha']>.99 and abs(fast['top'])<3,fast
            page.screenshot(path=str(OUT/f'{name}-{w}-hold.png'))
            scene.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*.15,behavior:'instant'})")
            page.wait_for_timeout(750)
            assert float(copy.evaluate("e=>getComputedStyle(e).opacity"))<.02
            results.append({'hold':hold,'browser':name,'width':w})
            results.append({'browser':name,'width':w,'height':h,'opacity':[a,b,c]})
        else:
            assert '0.62s' not in duration,duration
            results.append({'browser':name,'width':w,'reduced':reduced,'duration':duration})
        assert not errors,errors
    finally:page.close()
with sync_playwright() as p:
    for name in ['chromium','webkit']:
        b=getattr(p,name).launch()
        for w,h in [(375,812),(390,844)]:check(b,name,w,h,True)
        check(b,name,1440,900,False)
        check(b,name,375,812,True,True)
        b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
