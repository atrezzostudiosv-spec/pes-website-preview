import json
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path('film-reference');OUT.mkdir(exist_ok=True)
URL='https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-SEC-005'
results=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    for w in [375,390,768,1024,1180,1181,1440,1920]:
        page=b.new_page(viewport={'width':w,'height':844 if w<768 else 900})
        page.goto(URL,wait_until='domcontentloaded')
        page.wait_for_timeout(500)
        frames=[f for f in page.frames if f.locator('[data-atz-id="ATZ-SEC-005"] .ats2-film-scene').count()]
        assert frames, 'source demo not found'
        f=frames[-1];root=f.locator('[data-atz-id="ATZ-SEC-005"]')
        root.locator('.ats2-film-scene').wait_for()
        f.wait_for_function("document.querySelector('[data-atz-id=\"ATZ-SEC-005\"]').classList.contains('ats2-enhanced')")
        for q in [0,.25,.5,.75,1,.5,0]:
            f.evaluate("""q=>{const s=document.querySelector('.ats2-film-scene');window.scrollTo({top:s.getBoundingClientRect().top+scrollY+q*(s.offsetHeight-innerHeight),behavior:'instant'})}""",q)
            page.wait_for_timeout(300)
            v=f.evaluate("""()=>{let s=document.querySelector('.ats2-film-scene'),h=s.querySelector('.ats2-film-header'),t=s.querySelector('.ats2-film-track'),v=s.querySelector('.ats2-film-viewport'),title=s.querySelector('h2'),st=s.querySelector('.ats2-stage'),a=s.querySelector('article');return {p:s.dataset.ats2Progress,active:s.dataset.ats2Active,x:parseFloat(s.style.getPropertyValue('--ats2-film-x')),distance:t.scrollWidth-v.clientWidth,scene:s.offsetHeight,stage:st.offsetHeight,header:h.offsetHeight,title:title.offsetHeight,titleFont:getComputedStyle(title).fontSize,titleLine:getComputedStyle(title).lineHeight,titleWidth:title.getBoundingClientRect().width,frame:a.offsetHeight,frameWidth:a.offsetWidth,viewport:innerWidth,innerHeight:innerHeight,sticky:getComputedStyle(st).position}}""")
            results.append({'w':w,'q':q,**v})
            page.screenshot(path=str(OUT/f'{w}-{len(results)}.png'))
        page.close()
    b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results),flush=True)
