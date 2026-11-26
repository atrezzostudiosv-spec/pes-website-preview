"""Real-browser review evidence; no claim of visual approval from assertions."""
import json, threading, traceback
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa-evidence'; OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
DEMO='https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/components/originales/atrezzo/ATZ-SEC-016/index.html'
WIDTHS=[375,390,768,1024,1180,1181,1440,1920]
ROUTES=['','about/','portfolio/','hillside/','capabilities/','capabilities/lighting-systems/','capabilities/automated-window-coverings/','capabilities/lighting-design/','capabilities/power-quality-and-energy-management/','capabilities/ev-charging/','careers/','careers/foreman/','careers/journeyman/','careers/electrician/','careers/apprentice/','contact/']
results=[]; failures=[]
def require(cond,msg):
    if not cond: raise AssertionError(msg)
def state(page):
    return page.evaluate("""()=>{const h=document.querySelector('.site-header'),hero=document.querySelector('.hero-film'),logo=h.querySelector('.logo-light'),nav=h.querySelector('.site-nav'),trigger=h.querySelector('.menu-trigger'),c=hero?.querySelector('.hero-content'),r=h.getBoundingClientRect(),cs=getComputedStyle(h);return {scroll:scrollY,scrolled:h.classList.contains('is-scrolled'),hidden:h.classList.contains('is-hidden'),inert:h.inert,headerHeight:r.height,headerBg:cs.backgroundColor,headerTop:r.top,headerFilter:cs.backdropFilter,navDisplay:getComputedStyle(nav).display,menuDisplay:getComputedStyle(trigger).display,logoWidth:logo.getBoundingClientRect().width,logoLoaded:logo.complete&&logo.naturalWidth>0,logoNative:logo.naturalWidth,heroHeight:hero?.getBoundingClientRect().height,heroBottom:c?getComputedStyle(c).bottom:null,heroFont:hero?getComputedStyle(hero.querySelector('h1')).fontSize:null,heroFamily:hero?getComputedStyle(hero.querySelector('h1')).fontFamily:null,bodyFamily:getComputedStyle(document.body).fontFamily,viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,engineCount:document.querySelectorAll('script[src$="engine.original.js"]').length,videoCount:document.querySelectorAll('video').length,headerCount:document.querySelectorAll('header.site-header').length,modalCount:document.querySelectorAll('#menu-dialog').length,mainCount:document.querySelectorAll('main').length,headerOverflow:[...h.children].some(e=>e.getBoundingClientRect().right>innerWidth+1),active:!!h.querySelector('[aria-current="page"],[data-section-active="true"]')}}""")
def scroll(page,y): page.evaluate("(y)=>window.scrollTo({top:y,behavior:'instant'})",y);page.wait_for_timeout(400)
def shot(page,label): page.screenshot(path=str(OUT/(label+'.png')),animations='allow',timeout=15000)
def inspect(browser,kind,url,w,full=True,reduce=False):
    page=browser.new_page(viewport={'width':w,'height':900 if w>=768 else 844},device_scale_factor=1,reduced_motion='reduce' if reduce else 'no-preference')
    errors=[]; bad=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:bad.append({'status':r.status,'url':r.url}) if r.status>=400 and (urlparse(r.url).netloc==urlparse(url).netloc) else None)
    rec={'kind':kind,'url':url,'width':w,'reduced':reduce}
    try:
        response=page.goto(url,wait_until='domcontentloaded',timeout=30000)
        require(response and response.ok,'navigation failed')
        page.locator('.site-header').wait_for()
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        rec['top']=top=state(page)
        require(top['headerCount']==1 and top['modalCount']==1,'duplicate header/modal')
        require(top['logoLoaded'],'logo failed to load')
        require(top['navDisplay']=='none' if w<=1180 else top['navDisplay']!='none','desktop breakpoint')
        require(top['menuDisplay']!='none' if w<=1180 else top['menuDisplay']=='none','mobile breakpoint')
        require(not top['headerOverflow'],'header overflows viewport')
        require(not top['scrolled'] and not top['hidden'],'incorrect top state')
        if kind.startswith('pes'):
            require(top['logoNative']==720,'wrong logo')
            require(abs(top['logoWidth']-(135 if w<=767 else 155 if w<=1180 else 180))<2,'wrong logo width')
            require('Montserrat' in top['bodyFamily'],'body family mismatch')
            require(top['active'],'no active page/section')
            require(page.evaluate("document.fonts.check('300 20px Montserrat') && document.fonts.check('700 20px Montserrat')"),'local Montserrat unavailable')
            if top['videoCount']:
                rec['editorial']=page.locator('.hero-film h1').evaluate("""e=>{const s=getComputedStyle(e),r=getComputedStyle(e,'::after'),b=e.getBoundingClientRect(),c=e.closest('.hero-content').getBoundingClientRect(),h=e.closest('.hero-film').getBoundingClientRect();return {light:s.fontWeight,bold:getComputedStyle(e.querySelector('strong')).fontWeight,ruleWidth:r.width,ruleHeight:r.height,ruleColor:r.backgroundColor,headlineTop:b.top,contentTop:c.top,contentBottom:c.bottom,heroBottom:h.bottom,overflow:e.scrollWidth>e.clientWidth+2,overlap:c.top<document.querySelector('.site-header').getBoundingClientRect().bottom}}""")
                require(rec['editorial']['light']=='300' and rec['editorial']['bold']=='700','hero weights')
                require(rec['editorial']['ruleHeight']=='2px','hero rule')
                require(not rec['editorial']['overflow'] and not rec['editorial']['overlap'],'hero text overflow/overlap '+str(rec['editorial']))
            require(top['engineCount']==1,'duplicate or missing engine')
            require(top['videoCount']==(1 if url==BASE else 0),'unexpected video')
        if full:
            if top['videoCount']:
                if reduce:
                    require(page.locator('[data-hero-video-toggle]').is_disabled(),'reduced motion toggle not disabled')
                    require(page.locator('video').evaluate('(v)=>v.paused'),'reduced motion video playing')
                else:
                    page.wait_for_function("document.querySelector('video').readyState>=2",timeout=12000)
                    btn=page.locator('[data-hero-video-toggle]')
                    # Ensure button can pause and resume whether autoplay was permitted or not.
                    if page.locator('video').evaluate('(v)=>v.paused'): btn.click();page.wait_for_timeout(500)
                    require(not page.locator('video').evaluate('(v)=>v.paused'),'play failed')
                    btn.click();page.wait_for_timeout(150)
                    require(page.locator('video').evaluate('(v)=>v.paused'),'pause failed')
                    rec['film']='play/pause passed'
            shot(page,f'{kind}-{w}-top'+('-reduced' if reduce else ''))
            scroll(page,66)
            rec['scroll66']=s=state(page);require(s['scrolled'] and not s['hidden'],'65px glass threshold failed')
            shot(page,f'{kind}-{w}-glass')
            scroll(page,400);rec['down']=s=state(page);require(s['hidden'] and s['inert'],'down hide failed')
            shot(page,f'{kind}-{w}-hidden')
            scroll(page,370);rec['up']=s=state(page);require(not s['hidden'] and not s['inert'],'up reveal failed')
            shot(page,f'{kind}-{w}-up')
            scroll(page,0)
            if w>1180:
                details=page.locator('.site-header details[data-header-nav]').first
                details.locator('summary').hover();page.wait_for_timeout(250)
                require(details.evaluate('(e)=>e.open'),'hover dropdown failed')
                shot(page,f'{kind}-{w}-dropdown')
                page.keyboard.press('Escape')
                require(not details.evaluate('(e)=>e.open'),'Escape dropdown failed')
                details.locator('summary').focus();page.keyboard.press('Enter')
                require(details.evaluate('(e)=>e.open'),'keyboard dropdown failed')
                page.keyboard.press('Escape')
            else:
                page.locator('[data-open="menu-dialog"]').click();page.wait_for_timeout(600)
                require(page.locator('#menu-dialog').evaluate('(e)=>e.open'),'mobile modal failed')
                shot(page,f'{kind}-{w}-menu')
                page.locator('#menu-dialog .menu-group summary').first.click()
                require(page.locator('#menu-dialog .menu-group').first.evaluate('(e)=>e.open'),'mobile submenu failed')
                shot(page,f'{kind}-{w}-submenu')
                page.keyboard.press('Escape');page.wait_for_timeout(100)
                require(not page.locator('#menu-dialog').evaluate('(e)=>e.open'),'modal Escape failed')
                require(page.evaluate("document.body.style.overflow!== 'hidden'"),'scroll locked after modal')
        rec['errors']=errors;rec['badResponses']=bad
        require(not errors,'page errors: '+str(errors))
        require(not bad,'asset failures: '+str(bad))
        rec['status']='passed'
    except Exception as e:
        rec['status']='failed';rec['failure']=str(e);rec['errors']=errors;rec['badResponses']=bad
        failures.append(f'{kind} {w} {url}: {e}')
        try: shot(page,f'{kind}-{w}-failure-{len(failures)}')
        except Exception: pass
    finally:
        page.close();results.append(rec);print(json.dumps(rec),flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--autoplay-policy=no-user-gesture-required'])
    for w in WIDTHS:
        inspect(browser,'reference',DEMO,w)
        inspect(browser,'pes-home',BASE,w)
        inspect(browser,'pes-about',BASE+'about/',w,full=True)
    for r in ROUTES[2:]:
        for w in [375,1440]: inspect(browser,'pes-route',BASE+r,w,full=False)
    inspect(browser,'pes-reduced',BASE,375,full=True,reduce=True)
    browser.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
for f in failures: print(f,flush=True)
if failures: raise SystemExit(1)
