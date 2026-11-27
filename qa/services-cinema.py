import hashlib, threading, json, re
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'services-qa';OUT.mkdir(exist_ok=True)
def blob(p):
    b=p.read_bytes();return hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()
assert blob(ROOT/'assets/atz-sec-015/engine.original.js')=='d81debdcc6448ec37aee08b71bde0a9fa0e000c1'
assert blob(ROOT/'assets/atz-sec-015/component.css')=='835956afd7c453774bd4bd06712a1d14ccff7595'
assert blob(ROOT/'assets/vendor/ats2-engine.js')=='dbc50858a0e026a0941587b1885a99eaa6ab2111'
assert blob(ROOT/'assets/vendor/ATZ-SEC-004.js')=='b8cd6629e23e528a16363b61d9f31730124b1786'
pages=[p for p in ROOT.rglob('index.html') if 'assets' not in p.relative_to(ROOT).parts]
assert len(pages)==16
for p in pages:assert not re.search(r'launching\s+soon',p.read_text(),re.I),p
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=s.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{s.server_port}/'
SEL='.pes-services-cinema'
slugs=["lighting-systems","automated-window-coverings","lighting-design","power-quality-and-energy-management","ev-charging"]
results=[]
def test(b,name,w,h,mode='animated'):
    p=b.new_page(viewport={'width':w,'height':h},java_script_enabled=mode!='nojs',reduced_motion='reduce' if mode=='reduced' else 'no-preference',has_touch=w<768)
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
        assert p.goto(BASE,wait_until='load',timeout=45000).ok
        p.evaluate('document.fonts.ready')
        sec=p.locator(SEL);assert sec.count()==1
        assert sec.locator('[data-collection-panel]').count()==5
        assert sec.locator('[data-collection-tab]').count()==5
        assert sec.locator('.collection-all-homes,.collection-fallback-link').count()==0
        assert sec.evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(0, 0, 0)'
        assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
        for i,slug in enumerate(slugs):
            assert sec.locator('[data-collection-panel]').nth(i).locator('h3 a').get_attribute('href')=='capabilities/'+slug+'/'
            assert p.request.get(BASE+'capabilities/'+slug+'/').ok
            image=sec.locator('.collection-photo').nth(i).get_attribute('src')
            assert p.request.get(BASE+image).ok
        if mode=='animated':
            p.wait_for_function("document.querySelector('[data-pes-services-intro]').dataset.pesServicesMotion")
            intro=sec.locator('[data-pes-services-intro]')
            intro.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-100,behavior:'instant'})")
            p.wait_for_function("document.querySelector('[data-pes-services-intro]').dataset.pesServicesMotion==='playing'")
            p.wait_for_function("document.querySelectorAll('.pes-services-title-overlay .am-char').length>0")
            def title_geometry():
                return intro.evaluate("""e=>{const h=e.querySelector('h2'),b=h.getBoundingClientRect();return [...h.querySelectorAll('.pes-services-title-line')].map(l=>{const r=l.getBoundingClientRect();return [r.left-b.left,r.top-b.top,r.width,r.height]})}""")
            during=title_geometry()
            assert intro.locator('.pes-services-title-overlay .am-char').evaluate_all("els=>els.every(e=>getComputedStyle(e).position==='absolute'&&e.style.left!=='')"),during
            if w in [390,1440]:p.screenshot(path=str(OUT/f'{name}-{w}-intro-motion.jpg'),type='jpeg',quality=80)
            p.wait_for_function("document.querySelector('[data-pes-services-intro]').dataset.pesServicesMotion==='complete'")
            after=title_geometry()
            assert all(abs(a-b)<1 for l1,l2 in zip(during,after) for a,b in zip(l1,l2)),(during,after)
            assert intro.locator('.pes-services-title-overlay,[data-pes-services-pending]').count()==0
            assert intro.locator('h2').evaluate("e=>[...e.querySelectorAll('.pes-services-title-line')].every(l=>getComputedStyle(l).opacity==='1'&&l.scrollWidth<=l.clientWidth+1)")
            if w in [390,1440]:p.screenshot(path=str(OUT/f'{name}-{w}-intro-final.jpg'),type='jpeg',quality=80)
            p.wait_for_function("document.querySelector('.pes-services-cinema').classList.contains('is-cinema-active')")
            p.wait_for_function("ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))")
            p.evaluate("()=>{const t=document.querySelector('[data-collection-track]');window.scrollTo({top:t.getBoundingClientRect().top+scrollY+10,behavior:'instant'})}")
            p.wait_for_timeout(700)
            for i in [0,1,2,3,4,2,0]:
                p.locator('[data-collection-tab]').nth(i).click()
                p.wait_for_function("i=>document.querySelector('[data-collection-tab=\"'+i+'\"]').getAttribute('aria-selected')==='true'",arg=i)
                p.wait_for_timeout(220)
                state=sec.evaluate("""r=>{const stage=r.querySelector('[data-collection-stage]'),active=r.querySelector('[data-collection-panel][aria-hidden=false]'),title=active.querySelector('h3'),bottom=r.querySelector('.collection-bottom'),box=e=>e.getBoundingClientRect();return {stageTop:box(stage).top,stageHeight:box(stage).height,titleBottom:box(title).bottom,bottomTop:box(bottom).top,tabWidths:[...r.querySelectorAll('[data-collection-tab]')].map(e=>box(e).width),active:active.id,scale:getComputedStyle(active.querySelector('img')).transform,counter:r.querySelector('[data-collection-counter]').textContent,cta:r.querySelector('[data-collection-property-link]').getAttribute('href'),overflow:document.documentElement.scrollWidth>innerWidth}}""")
                assert abs(state['stageTop'])<4 and state['stageHeight']>h*.95,state
                assert state['titleBottom']<state['bottomTop'] and min(state['tabWidths'])>=44,state
                assert state['counter']==f'{i+1:02d} / 05' and state['cta']=='capabilities/'+slugs[i]+'/' and not state['overflow'],state
                if w in [390,1440] and i in [0,2,3,4]:p.screenshot(path=str(OUT/f'{name}-{w}-{i+1}.jpg'),type='jpeg',quality=80)
            p.locator('[data-collection-tab]').first.focus()
            p.keyboard.press('End')
            p.wait_for_function("document.querySelector('[data-collection-counter]').textContent==='05 / 05'")
            p.keyboard.press('Home')
            p.wait_for_function("document.querySelector('[data-collection-counter]').textContent==='01 / 05'")
        else:
            assert not sec.evaluate("e=>e.classList.contains('is-cinema-active')")
            if mode in ['nojs','reduced']:assert sec.locator('.pes-services-title-line').evaluate_all("els=>els.every(e=>getComputedStyle(e).opacity==='1')")
            assert sec.locator('[data-collection-panel][aria-hidden=false]').count()==5
            assert all(x>0 for x in sec.locator('[data-collection-panel]').evaluate_all("els=>els.map(e=>e.getBoundingClientRect().height)"))
        # Home 05: shared two-column introduction, independent one-shot motion, original Handoff.
        diff=p.locator('#pes-difference')
        assert diff.count()==1
        assert diff.locator('h2').get_attribute('aria-label')=='Beyond what you see.'
        assert diff.evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(0, 0, 0)'
        assert diff.evaluate("e=>e.previousElementSibling.id==='pes-services'&&e.nextElementSibling.dataset.atzId==='ATZ-SEC-004'")
        layout=diff.locator('.collection-intro').evaluate("""e=>{const b=e.getBoundingClientRect(),h=e.querySelector('h2').getBoundingClientRect(),p=e.querySelector(':scope>p').getBoundingClientRect();return {heading:[h.left-b.left,h.top-b.top,h.width,h.height],copy:[p.left-b.left,p.top-b.top,p.width,p.height],display:getComputedStyle(e).display,font:getComputedStyle(e.querySelector('h2')).fontSize}}""")
        assert layout['display']==('grid' if w>767 else 'block'),layout
        assert layout['copy'][0]>layout['heading'][0] if w>767 else layout['copy'][1]>layout['heading'][1],layout
        if mode=='animated':
            diff.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-70,behavior:'instant'})")
            diff_intro=diff.locator('[data-pes-services-intro]')
            p.wait_for_function("document.querySelector('#pes-difference [data-pes-services-intro]').dataset.pesServicesMotion==='playing'")
            p.wait_for_function("document.querySelectorAll('#pes-difference .pes-services-title-overlay .am-char').length>0")
            geom=lambda:diff_intro.evaluate("""e=>{const h=e.querySelector('h2'),b=h.getBoundingClientRect();return [...h.querySelectorAll('.pes-services-title-line')].map(l=>{const r=l.getBoundingClientRect();return [r.left-b.left,r.top-b.top,r.width,r.height]})}""")
            before=geom()
            if w in [390,1440]:p.screenshot(path=str(OUT/f'{name}-{w}-difference-motion.jpg'),type='jpeg',quality=80)
            p.wait_for_function("document.querySelector('#pes-difference [data-pes-services-intro]').dataset.pesServicesMotion==='complete'")
            after=geom()
            assert all(abs(a-b)<1 for l1,l2 in zip(before,after) for a,b in zip(l1,l2)),(before,after)
            assert diff.locator('.pes-services-title-overlay,[data-pes-services-pending]').count()==0
            assert diff.locator('.pes-services-title-line').evaluate_all("els=>els.every(e=>getComputedStyle(e).opacity==='1'&&e.scrollWidth<=e.clientWidth+1)")
            if w in [390,1440]:p.screenshot(path=str(OUT/f'{name}-{w}-difference-final.jpg'),type='jpeg',quality=80)
            handoff=p.locator('#ats2-handoff')
            if w>820:
                p.wait_for_function("document.querySelector('[data-atz-id=\\\"ATZ-SEC-004\\\"]').classList.contains('ats2-enhanced')")
                for progress in [0,.5,1,.25]:
                    handoff.evaluate("(e,p)=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*p,behavior:'instant'})",progress)
                    p.wait_for_timeout(300)
                    data=handoff.evaluate("""e=>({p:+e.dataset.ats2Progress,wipe:parseFloat(e.style.getPropertyValue('--ats2-wipe')),first:+e.style.getPropertyValue('--ats2-first-copy'),second:+e.style.getPropertyValue('--ats2-second-copy')})""")
                    assert abs(data['p']-progress)<.025,data
                    if progress==0:assert data['wipe']>99 and data['first']>.99,data
                    if progress==.5:assert 0<data['wipe']<100,data
                    if progress==1:assert data['wipe']<1 and data['second']>.99,data
                    if w==1440:p.screenshot(path=str(OUT/f'{name}-{w}-handoff-{progress}.jpg'),type='jpeg',quality=80)
            else:assert handoff.locator('.ats2-handoff-pane').count()==2
        elif mode in ['nojs','reduced']:
            assert diff.locator('.pes-services-title-line').evaluate_all("els=>els.every(e=>getComputedStyle(e).opacity==='1')")
        assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
        assert not errors,errors
        results.append({'browser':name,'width':w,'height':h,'mode':mode})
    finally:p.close()
with sync_playwright() as pw:
    for name in ['chromium','webkit']:
        b=getattr(pw,name).launch(headless=True)
        for w,h in [(375,844),(390,844),(768,900),(1024,768),(1440,900),(1920,1080)] if name=='chromium' else [(390,844),(1440,900)]:
            test(b,name,w,h)
        for mode in ['nojs','reduced','short']:
            test(b,name,390,650 if mode=='short' else 844,mode)
        b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
