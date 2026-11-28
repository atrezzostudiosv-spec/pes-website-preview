"""Focused navigation and rendering checks for the PES V3 review preview."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import json
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            pass

server = ThreadingHTTPServer(("127.0.0.1", 0), lambda *a, **kw: Quiet(*a, directory=str(ROOT), **kw))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}"
ROUTES = ["/", "/about/"] + [p["route"] for p in json.loads((ROOT / "data/editorial-v3.json").read_text())["pages"]]
VIEWPORTS = [(375, 812), (390, 844), (768, 900), (1024, 900), (1440, 900)]


def run(browser_type, executable_path=None):
    results = []
    browser = browser_type.launch(headless=True, executable_path=executable_path)
    for width, height in VIEWPORTS:
        context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        for route in ROUTES:
            errors.clear()
            response = page.goto(BASE + route, wait_until="domcontentloaded")
            page.wait_for_timeout(100)
            h1 = page.locator("main h1").count()
            overflow = page.evaluate("document.documentElement.scrollWidth - innerWidth")
            missing = page.locator("main img").evaluate_all("images => images.filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)")
            result = {"route": route, "width": width, "status": response.status if response else None, "h1": h1, "overflow": overflow, "missing_images": missing, "page_errors": errors}
            results.append(result)
            if result["status"] != 200 or h1 != 1 or overflow > 1 or missing or errors:
                print(result)
        context.close()
    browser.close()
    return results


try:
    with sync_playwright() as p:
        engine = sys.argv[1] if len(sys.argv) > 1 else "chromium"
        if engine == "chromium":
            executable = "/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None
            results = run(p.chromium, executable)
        elif engine == "webkit":
            results = run(p.webkit)
        else:
            raise SystemExit("Use chromium or webkit")
finally:
    server.shutdown()

failures = [r for r in results if r["status"] != 200 or r["h1"] != 1 or r["overflow"] > 1 or r["missing_images"] or r["page_errors"]]
print(f"{engine}: {len(results)} route/viewport checks, {len(failures)} failures")
raise SystemExit(bool(failures))
