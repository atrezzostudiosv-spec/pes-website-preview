from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
server=ThreadingHTTPServer(("127.0.0.1",0),SimpleHTTPRequestHandler)
Thread(target=server.serve_forever,daemon=True).start()
base=f"http://127.0.0.1:{server.server_port}"
pages=sorted(p for p in ROOT.rglob("index.html") if "assets" not in p.relative_to(ROOT).parts and ".git" not in p.relative_to(ROOT).parts)
assert len(pages)==16
os.makedirs("flat-logo-qa",exist_ok=True)
with sync_playwright() as pw:
 for engine in (pw.chromium,pw.webkit):
  browser=engine.launch()
  for w,h in [(1440,900),(1024,768),(768,1024),(390,844),(320,667)]:
   page=browser.new_page(viewport={"width":w,"height":h},reduced_motion="reduce")
   for path in (pages if w in (1440,390) else [ROOT/"index.html"]):
    url=base+"/"+str(path.relative_to(ROOT))
    page.goto(url,wait_until="domcontentloaded")
    page.evaluate("document.fonts.ready")
    page.wait_for_function("Array.from(document.querySelectorAll('.site-header .brand img, .ui.footer img.logo, .menu-dialog .brand img')).every(i=>i.complete&&i.naturalWidth>0)")
    brand=page.locator(".site-header>.brand").bounding_box()
    header=page.locator(".site-header").bounding_box()
    assert brand and header and abs(brand["x"]+brand["width"]/2-w/2)<2,(engine.name,w,path,brand)
    assert abs(brand["y"]+brand["height"]/2-(header["y"]+header["height"]/2))<2,(engine.name,w,path,brand,header)
    for item in page.locator(".site-header .pes-nav-left>a, .site-header .pes-nav-right>details, .site-header .pes-nav-right>a, .site-header .header-phone, .site-header .menu-trigger").all():
     if not item.is_visible(): continue
     b=item.bounding_box()
     assert b and (b["x"]+b["width"]<=brand["x"]+1 or b["x"]>=brand["x"]+brand["width"]-1),(engine.name,w,path,item.inner_text(),b,brand)
    assert page.locator(".ui.footer img.logo").get_attribute("src").endswith("pes-logo-flat.svg")
    if path==ROOT/"index.html":
     page.screenshot(path=f"flat-logo-qa/{engine.name}-{w}.png")
   page.close()
  browser.close()
print("PES flat logo geometry and resource checks passed")
