import base64,json,threading,subprocess,math
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,devices
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'cinematic-qa';OUT.mkdir(exist_ok=True)
VIDEOS=OUT/'videos';VIDEOS.mkdir(exist_ok=True)
OLD=Path('/tmp/pes-cinematic-v10');subprocess.run(['git','worktree','add','--detach',str(OLD),'ec9c289e011df9de0f35b9f75545040392792bed'],cwd=ROOT,check=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
def serve(path):
    s=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(path),**kw));threading.Thread(target=s.serve_forever,daemon=True).start();return f'http://127.0.0.1:{s.server_port}/'
BASE=serve(ROOT);PREV=serve(OLD);SEL='.pes-cinematic-interlude'
results=[];failures=[]
def go(p,url):
    assert p.goto(url,wait_until='load',timeout=45000).ok
    p.evaluate('document.fonts.ready')
def state(p):
    return p.evaluate("""()=>{const r=document.querySelector('.pes-cinematic-interlude'),g=r.querySelector('.grid'),t=r.querySelector('.content__title'),h=t.querySelector('h2'),service=document.querySelector('.art-atlas'),pin=ScrollTrigger.getById('pes-cinematic-pin')||ScrollTrigger.getAll().find(x=>x.pin===r),entry=ScrollTrigger.getById('pes-cinematic-entry'),exit=ScrollTrigger.getById('pes-cinematic-exit'),box=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,bottom:b.bottom}};return {y:scrollY,vh:innerHeight,root:box(r),services:box(service),header:box(document.querySelector('.site-header')),pin:pin&&{start:pin.start,end:pin.end,p:pin.progress},entry:entry?.progress,exit:exit?.progress,alpha:[...g.children].map(e=>+getComputedStyle(e).opacity),scale:+gsap.getProperty(g,'scaleX'),skew:+gsap.getProperty(g,'skewY'),title:+getComputedStyle(t).opacity,titleBox:box(t),black:+(getComputedStyle(r).getPropertyValue('--pes-cinematic-black')||0),overflow:document.documentElement.scrollWidth>innerWidth,weights:[getComputedStyle(h).fontWeight,getComputedStyle(h.querySelector('strong')).fontWeight],servicesBg:getComputedStyle(service).backgroundColor,triggerCount:ScrollTrigger.getAll().filter(x=>x.vars.id?.startsWith('pes-cinematic-')).length}}""")
def scroll_to(p,y):
    p.evaluate("(y)=>window.scrollTo({top:y,behavior:'instant'})",y);p.wait_for_timeout(250)
def travel(p,target,duration=4500):
    # Continuous native scroll position updated at each animation frame, no progress seeks.
    return p.evaluate("""async ({target,duration})=>{const y=scrollY,t0=performance.now(),out=[];let last=0;await new Promise(resolve=>{function frame(t){const q=Math.min(1,(t-t0)/duration);window.scrollTo({top:y+(target-y)*q,behavior:'instant'});if(t-last>85){const r=document.querySelector('.pes-cinematic-interlude'),g=r.querySelector('.grid'),pin=ScrollTrigger.getById('pes-cinematic-pin'),s=document.querySelector('.art-atlas');out.push({y:scrollY,top:r.getBoundingClientRect().top,services:s.getBoundingClientRect().top,alpha:[...g.children].map(e=>+getComputedStyle(e).opacity),scale:+gsap.getProperty(g,'scaleX'),black:+(getComputedStyle(r).getPropertyValue('--pes-cinematic-black')||0),p:pin?.progress});last=t;}if(q<1)requestAnimationFrame(frame);else resolve();}requestAnimationFrame(frame)});return out;}""",{'target':target,'duration':duration})
def record(b,name,w,h,old=False):
    tag=('v10-' if old else 'v11-')+name+'-'+str(w)
    options={'viewport':{'width':w,'height':h},'device_scale_factor':1,'has_touch':w<=700}
    if w<=700:options.update({'is_mobile':True,'user_agent':('Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1' if name=='webkit' else 'Mozilla/5.0 (Linux; Android 15; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36')})
    capture=(w in [390,1440])
    if capture:options.update({'record_video_dir':str(VIDEOS),'record_video_size':{'width':w,'height':h}})
    ctx=b.new_context(**options);p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    try:
        go(p,PREV if old else BASE);p.wait_for_function("window.ScrollTrigger && document.querySelector('.pes-cinematic-interlude').classList.contains('pes-cinematic-animated')",timeout=20000)
        p.wait_for_function("ScrollTrigger.getAll().some(t=>t.pin===document.querySelector('.pes-cinematic-interlude'))")
        s=state(p);pin=s['pin'];vh=s['root']['h']
        if not old:
            assert s['triggerCount']==3 and s['weights']==['300','700'] and not s['overflow'],s
            assert abs(pin['end']-pin['start']-vh*(1 if w<=700 else 1.5))<5,s
            assert s['servicesBg']=='rgb(0, 0, 0)',s
            assert p.locator(SEL+' .grid__img').count()==9
            assert p.locator(SEL).evaluate("""async r=>{const u=[...r.querySelectorAll('.grid__img')].map(e=>getComputedStyle(e).backgroundImage.slice(5,-2));return (await Promise.all(u.map(async x=>{const i=new Image();i.src=x;await i.decode();return i.naturalWidth>0}))).every(Boolean)}""")
        scroll_to(p,pin['start']-vh*.92)
        p.screenshot(path=str(OUT/(tag+'-approach.jpg')),type='jpeg',quality=83)
        down=travel(p,pin['start'],2200);p.wait_for_timeout(250);atpin=state(p);p.screenshot(path=str(OUT/(tag+'-entry.jpg')),type='jpeg',quality=83)
        middle=travel(p,pin['start']+(pin['end']-pin['start'])*.55,2000);p.wait_for_timeout(250);mid=state(p);p.screenshot(path=str(OUT/(tag+'-middle.jpg')),type='jpeg',quality=83)
        hold=travel(p,pin['end']-5,2000);p.wait_for_timeout(250);last=state(p);p.screenshot(path=str(OUT/(tag+'-hold.jpg')),type='jpeg',quality=83)
        exit=travel(p,pin['end']+vh*.55,1600);p.wait_for_timeout(250);ex=state(p);p.screenshot(path=str(OUT/(tag+'-exit.jpg')),type='jpeg',quality=83)
        tail=travel(p,pin['end']+vh*1.04,1200);p.wait_for_timeout(250);end=state(p);p.screenshot(path=str(OUT/(tag+'-services.jpg')),type='jpeg',quality=83)
        reverse=travel(p,pin['start']-vh*.92,6200);p.wait_for_timeout(200);back=state(p)
        if not old:
            assert min(atpin['alpha'])>.97 and atpin['scale']<.8 and atpin['black']<.02,atpin
            assert mid['scale']>atpin['scale']+.1 and mid['title']>.95,mid
            assert last['scale']>.99 and last['black']<.02 and last['title']>.95,last
            assert .35<ex['black']<.85 and ex['services']['y']<vh*.6,ex
            assert end['black']>.98,end
            assert back['scale']<.8 and back['black']<.02 and max(back['alpha'])>=.54,back
            assert any(min(t['alpha'])<max(t['alpha'])-.05 for t in down),down
            assert all(min(t['alpha'])>=.54 for t in down+middle+hold+exit+reverse)
            assert not errors,errors
            assert not any(x['overflow'] for x in [atpin,mid,last,ex,end,back])
        results.append({'name':tag,'initial':s,'entry':atpin,'middle':mid,'hold':last,'exit':ex,'end':end,'reverse':back,'samples':{'down':down,'middle':middle,'hold':hold,'exit':exit,'tail':tail,'reverse':reverse}})
    except Exception as e:
        failures.append({'name':tag,'error':str(e)});print('FAIL',tag,str(e)[:3000],flush=True)
        p.screenshot(path=str(OUT/(tag+'-failure.jpg')),type='jpeg',quality=83)
    finally:
        video=p.video;ctx.close()
        if video:video.save_as(VIDEOS/(tag+'.webm'));video.delete()
def fallback(b,w,reduce):
    p=b.new_page(viewport={'width':w,'height':844},java_script_enabled=reduce,reduced_motion='reduce' if reduce else 'no-preference')
    try:
        go(p,BASE);p.locator(SEL).scroll_into_view_if_needed()
        assert p.locator(SEL).evaluate("e=>!e.classList.contains('pes-cinematic-animated')&&getComputedStyle(e.querySelector('.grid')).opacity==='1'&&getComputedStyle(e.querySelector('.content__title')).opacity==='1'")
        assert p.locator(SEL+' .grid__img').count()==9
        assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
        results.append({'fallback':reduce,'width':w})
    except Exception as e:failures.append({'fallback':reduce,'width':w,'error':str(e)})
    finally:p.close()
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True)
    # Baseline reproduction and candidate runs use identical continuous paths.
    record(b,'chromium',1440,900,True);record(b,'chromium',390,844,True)
    for w,h in [(375,844),(390,844),(768,900),(1024,768),(1440,900),(1920,1080)]:record(b,'chromium',w,h)
    for w in [375,1440]:
        for reduce in [False,True]:fallback(b,w,reduce)
    b.close()
    b=pw.webkit.launch(headless=True)
    for w,h in [(375,844),(390,844)]:record(b,'webkit',w,h)
    b.close()
(OUT/'results.json').write_text(json.dumps({'results':results,'failures':failures},indent=2))
files=[OUT/f'{tag}-{phase}.jpg' for tag in ['v10-chromium-1440','v11-chromium-1440','v11-chromium-390','v11-webkit-390'] for phase in ['approach','entry','middle','hold','exit','services']]
sheet=Image.new('RGB',(1200,4*230),(18,18,18));d=ImageDraw.Draw(sheet)
for k,f in enumerate(files):
    if not f.exists():continue
    im=Image.open(f);im.thumbnail((195,205));x=(k%6)*200;y=(k//6)*230;sheet.paste(im,(x+(195-im.width)//2,y));d.text((x+2,y+208),f.stem.replace('chromium','chr'),fill='white')
sheet.save(OUT/'contact-sheet.jpg',quality=68)
print('EVIDENCE_THUMB '+base64.b64encode((OUT/'contact-sheet.jpg').read_bytes()).decode(),flush=True)
print('TOTAL',len(results),'FAILURES',len(failures),flush=True)
if failures:raise SystemExit(1)
