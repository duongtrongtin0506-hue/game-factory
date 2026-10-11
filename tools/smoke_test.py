# -*- coding: utf-8 -*-
"""Kiem ban web da build (dist/<game>/none) tren trinh duyet co man hinh dien thoai: python tools/smoke_test.py
Moi game: mo doc va ngang, cham vai cho, mo man dau va man cuoi qua moc ?level (chi co tac dung tren 127.0.0.1).
Hong khi: co loi console / loi JavaScript, canvas trong tron, hoac (Car Jam) bo giai trong game ra so buoc khac levels/.
In 1 dong moi game; thoat 1 neu co loi."""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# game -> cac duong dan thu them sau trang chinh
CASES = {
    "tap-arcade": ["?stage=1", "?stage=45"],
    "boba-sort": ["?level=1", "?level=100&win=1"],
    "car-jam": ["?level=1", "?level=LAST&win=1", "?screen=levels"],
    "tile-trio": ["?level=1", "?level=100&end=win"],
    "one-line": ["?level=1", "?level=100&win=1"],
}
COLORS = """() => { const c = document.querySelector('canvas'); if (!c || !c.width) return 0;
  const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data, seen = new Set();
  for (let i = 0; i < d.length; i += 4 * 97) seen.add(d[i] << 16 | d[i + 1] << 8 | d[i + 2]); return seen.size; }"""

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            super().do_GET()


def run():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT / "dist")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    car_levels = json.loads((ROOT / "levels" / "car-jam.json").read_text(encoding="utf-8"))
    results, failed = [], False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for game, extra in CASES.items():
            errors = []
            for w, h in ((390, 844), (844, 390)):
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=True, has_touch=True)
                page = ctx.new_page()
                page.on("console", lambda m: errors.append(f"console: {m.text[:160]}") if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(f"js: {str(e)[:160]}"))
                for path in [""] + extra:
                    page.goto(f"{base}/{game}/none/index.html{path.replace('LAST', str(len(car_levels)))}")
                    page.wait_for_timeout(700)
                    if page.evaluate(COLORS) < 4:
                        errors.append(f"canvas trong ({w}x{h} {path or 'trang chinh'})")
                    for x, y in ((0.5, 0.5), (0.5, 0.75), (0.3, 0.4)):
                        page.touchscreen.tap(w * x, h * y)
                        page.wait_for_timeout(150)
                if game == "car-jam" and w < h:
                    # bo giai trong game (dung cho goi y) phai ra dung so buoc it nhat ma tools/carjam.py da ghi
                    page.goto(f"{base}/{game}/none/index.html?selftest=1")
                    page.wait_for_function("document.title.startsWith('selftest:')", timeout=60000)
                    _, count, wrong = page.title().split(":")
                    if int(count) != len(car_levels):
                        errors.append("so man trong game khac levels/car-jam.json")
                    if wrong:
                        errors.append(f"bo giai trong game lech so buoc o man {wrong[:40]}")
                ctx.close()
            failed = failed or bool(errors)
            results.append(f"{game}: " + ("dat" if not errors else "LOI " + " | ".join(dict.fromkeys(errors))))
        browser.close()
    server.shutdown()
    return results, failed


if __name__ == "__main__":
    lines, bad = run()
    print("\n".join(lines))
    sys.exit(1 if bad else 0)
