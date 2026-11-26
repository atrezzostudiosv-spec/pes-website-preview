import json, threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'qa-evidence';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**k:Quiet(*a,directory=str(ROOT),**k))
threading.Thread(target=s.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{s.server_port}/'
LIVE='https://atrezzostudiosv-spec.github.io/pes-website-preview/?section02=44d90dd'
results=[]; failures=[]
def test(browser,w,url,mode='normal'):
    p=browser.new_page(viewport={'width':w,'height':900 if w>=768 else 844},reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    rec={'width':w,'url':url,'mode':mode}
    try:
        assert p.goto(url,wait_until='domcontentloaded',timeout=30000).ok
        sec=p.locator('section.pes-specialty');sec.wait_for(timeout=15000)
        p.evaluate("document.fonts.ready")
        assert sec.count()==1
        p.evaluate("document.querySelector('.pes-specialty').scrollIntoView({behavior:'instant',block:'start'})")
        p.wait_for_timeout(900)
        m=sec.evaluate("""e=>{const h=e.querySelector('h2'),b=h.querySelector('strong'),l=e.querySelector('.pes-specialty-label'),c=e.querySelector('.pes-specialty-copy'),g=e.querySelector('.pes-specialty-grid'),r=x=>{const a=x.getBoundingClientRect();return {x:a.x,y:a.y,width:a.width,height:a.height,right:a.right,bottom:a.bottom}};return {background:getComputedStyle(e).backgroundColor,font:getComputedStyle(h).fontFamily,light:getComputedStyle(h).fontWeight,bold:getComputedStyle(b).fontWeight,rule:getComputedStyle(h,'::after').width,thickness:getComputedStyle(h,'::after').height,ruleColor:getComputedStyle(h,'::after').backgroundColor,labelLine:getComputedStyle(l,'::before').backgroundColor,columns:getComputedStyle(g).gridTemplateColumns,heading:r(h),copy:r(c),section:r(e),scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,headlineOverflow:h.scrollWidth>h.clientWidth+2,copyOpacity:getComputedStyle(c).opacity,headingOpacity:getComputedStyle(h.parentElement).opacity,revealCount:e.querySelectorAll('.pes-specialty-enter').length,cta:e.querySelector('a').getAttribute('href'),next:e.nextElementSibling.nextElementSibling.className,heroCount:document.querySelectorAll('.hero-film').length,headerCount:document.querySelectorAll('.site-header').length}}""")
        rec['metrics']=m
        assert m['background']=='rgb(255, 255, 255)' and 'Montserrat' in m['font']
        assert m['light']=='300' and m['bold']=='700'
        assert m['rule']==('54px' if w<=480 else '76px') and m['thickness']=='2px'
        assert m['ruleColor']==m['labelLine']=='rgb(162, 253, 2)'
        assert m['scrollWidth']<=w and not m['headlineOverflow']
        assert m['heroCount']==m['headerCount']==1 and 'project-feature' in m['next']
        assert m['cta']=='about/' and m['copyOpacity']==m['headingOpacity']=='1'
        if w>900: assert m['copy']['x']>=m['heading']['right']-1
        else: assert m['copy']['y']>=m['heading']['bottom']
        if mode=='normal': assert m['revealCount']==2
        else: assert m['revealCount']==0
        assert not errors,errors
        prefix=('live' if url==LIVE else 'local')+f'-{w}-{mode}'
        sec.screenshot(path=str(OUT/(prefix+'-section.png')),timeout=15000)
        p.screenshot(path=str(OUT/(prefix+'-viewport.png')),timeout=15000)
        if w in [375,1440] and mode=='normal':
            p.evaluate("window.scrollTo({top:document.querySelector('.pes-specialty').getBoundingClientRect().bottom+scrollY-innerHeight*.55,behavior:'instant'})")
            p.wait_for_timeout(500);p.screenshot(path=str(OUT/(prefix+'-hillside-transition.png')))
            p.locator('.pes-specialty-link').focus()
            assert p.locator('.pes-specialty-link').evaluate('(e)=>document.activeElement===e')
            p.locator('.pes-specialty-link').press('Enter')
            p.wait_for_url('**/about/',timeout=10000)
        rec['status']='passed'
    except Exception as e:
        rec['status']='failed';rec['error']=str(e);failures.append(rec)
        try:p.screenshot(path=str(OUT/f'failure-{w}-{mode}.png'))
        except Exception:pass
    finally:
        results.append(rec);print(json.dumps(rec),flush=True);p.close()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    for w in [375,390,768,1024,1180,1181,1440,1920]:test(b,w,BASE)
    test(b,375,BASE,'reduced');test(b,1440,BASE,'no-js')
    test(b,1440,LIVE);test(b,375,LIVE)
    b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
if failures:raise SystemExit(1)
