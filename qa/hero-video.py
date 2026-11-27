import json, subprocess, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hero-video-qa'; OUT.mkdir(exist_ok=True)
VIDEO=ROOT/'assets/media/pes-hero-desktop.mp4'
assert VIDEO.stat().st_size==20976122
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(VIDEO)]))
v=next(s for s in meta['streams'] if s['codec_type']=='video')
assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080),v
assert not any(s['codec_type']=='audio' for s in meta['streams'])
assert 20<float(meta['format']['duration'])<23
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),lambda *a,**kw:Quiet(*a,directory=str(ROOT),**kw))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch()
  for w,h,mode in [(1728,1080,'normal'),(1440,900,'normal'),(1024,768,'normal'),(768,1024,'normal'),(375,812,'normal'),(390,844,'normal'),(390,844,'reduced'),(390,844,'no-js')]:
   page=b.new_page(viewport={'width':w,'height':h},has_touch=w<768,is_mobile=w<768,reduced_motion='reduce' if mode=='reduced' else 'no-preference',java_script_enabled=mode!='no-js')
   assert page.goto(url,wait_until='domcontentloaded',timeout=45000).ok
   video=page.locator('[data-hero-video]');button=page.locator('[data-hero-video-toggle]')
   assert video.locator('source').count()==1
   assert video.locator('source').get_attribute('src')=='assets/media/pes-hero-desktop.mp4'
   assert video.get_attribute('poster')=='assets/media/PES-002.jpg'
   assert video.evaluate('e=>e.muted&&e.loop&&e.playsInline')
   assert page.locator('.hero-film .hero-content .line-link').count()==0
   assert page.locator('.hero-film .scroll-cue').get_attribute('href')=='#pes-specialty'
   page.evaluate('document.fonts.ready')
   title=page.locator('.hero-film h1').evaluate("""e=>{const s=getComputedStyle(e),b=getComputedStyle(e.querySelector('strong')),r=e.getBoundingClientRect(),c=e.closest('.hero-content').getBoundingClientRect();return {size:parseFloat(s.fontSize),light:s.fontWeight,bold:b.fontWeight,left:r.left,right:r.right,contentRight:c.right,scroll:e.scrollWidth,width:e.clientWidth}}""")
   expected=min(54,max(34,w*.088)) if w<=767 else min(76,max(46,w*.066)) if w<=1100 else min(96,max(54,w*.059))
   assert abs(title['size']-expected)<.5 and title['light']=='300' and title['bold']=='700',title
   assert title['scroll']<=title['width']+1 and title['right']<=title['contentRight']+1,title
   if mode=='normal':
    page.wait_for_function("document.querySelector('[data-hero-video]').readyState>=2 && !document.querySelector('[data-hero-video]').paused && document.querySelector('[data-hero-video]').currentTime>0",timeout=45000)
    state=video.evaluate("e=>({src:e.currentSrc,width:e.videoWidth,height:e.videoHeight,time:e.currentTime,fit:getComputedStyle(e).objectFit})")
    assert state['src'].endswith('/assets/media/pes-hero-desktop.mp4') and state['width']==1920 and state['height']==1080 and state['fit']=='cover',state
    button.click()
    page.wait_for_function("document.querySelector('[data-hero-video]').paused")
    button.click()
    page.wait_for_function("!document.querySelector('[data-hero-video]').paused")
    page.screenshot(path=str(OUT/f'{engine}-{w}.png'))
   else:
    assert video.evaluate('e=>e.paused')
    if mode=='reduced':
     assert button.is_disabled()
    state={'static':True}
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   results.append({'engine':engine,'viewport':[w,h],'mode':mode,'state':state})
   page.close()
  b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('TOTAL',len(results),'FAILURES 0',flush=True)
