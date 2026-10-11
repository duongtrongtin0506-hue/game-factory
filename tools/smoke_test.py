# -*- coding: utf-8 -*-
"""Kiem ban web da build (dist/<game>/none) tren trinh duyet: python tools/smoke_test.py
Moi game: mo o co dien thoai doc, dien thoai ngang va may tinh (1280x720), cham (may tinh: bam chuot) vai cho, mo man dau va man cuoi qua moc ?level (chi co tac dung tren 127.0.0.1).
Hong khi: co loi console / loi JavaScript, canvas trong tron, (Car Jam) bo giai trong game ra so buoc khac levels/, (Boba Sort) bo giai trong game khong giai noi mot man, (Tile Trio) man co danh sach quan hong, (One Line Fill) duong di mau hong, hoac (Tap Arcade) chang co tro la / moc diem sai.
Do them thoi gian tai: mo lan dau tren may yeu (CPU cham 4 lan) qua mang cham (1,6 Mbit/s, tre 150 ms), tinh den luc canvas co hinh; qua LOAD_LIMIT giay la hong.
In 1 dong moi game (kem so giay tai); thoat 1 neu co loi."""
import functools
import http.server
import json
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# game -> cac duong dan thu them sau trang chinh
CASES = {
    "tap-arcade": ["?stage=1", "?stage=LAST"],
    "boba-sort": ["?level=1", "?level=LAST&win=1"],
    "car-jam": ["?level=1", "?level=LAST&win=1", "?screen=levels"],
    "tile-trio": ["?level=1", "?level=LAST&end=win"],
    "one-line": ["?level=1", "?level=LAST&win=1"],
}
LOAD_LIMIT = 5.0
SIZES = ((390, 844, True), (844, 390, True), (1280, 720, False))   # rong, cao, la dien thoai
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
    counts = {g: len(json.loads((ROOT / "levels" / f"{g}.json").read_text(encoding="utf-8"))) for g in CASES}
    results, failed = [], False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for game, extra in CASES.items():
            errors, load = [], 0.0
            for w, h, phone in SIZES:
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if phone else 1, is_mobile=phone, has_touch=phone)
                page = ctx.new_page()
                if w < h:
                    slow = ctx.new_cdp_session(page)
                    slow.send("Network.enable")
                    slow.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 200000, "uploadThroughput": 100000})
                    slow.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                    start = time.time()
                    page.goto(f"{base}/{game}/none/index.html")
                    try:
                        page.wait_for_function(f"({COLORS})() >= 4", timeout=20000)
                    except Exception:
                        pass
                    load = time.time() - start
                    if load > LOAD_LIMIT:
                        errors.append(f"tai {load:.1f} giay (gioi han {LOAD_LIMIT:.0f})")
                    slow.send("Network.emulateNetworkConditions", {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
                    slow.send("Emulation.setCPUThrottlingRate", {"rate": 1})
                page.on("console", lambda m: errors.append(f"console: {m.text[:160]}") if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(f"js: {str(e)[:160]}"))
                for path in [""] + extra:
                    page.goto(f"{base}/{game}/none/index.html{path.replace('LAST', str(counts.get(game, 0)))}")
                    page.wait_for_timeout(700)
                    if page.evaluate(COLORS) < 4:
                        errors.append(f"canvas trong ({w}x{h} {path or 'trang chinh'})")
                    for x, y in ((0.5, 0.5), (0.5, 0.75), (0.3, 0.4)):
                        (page.touchscreen.tap if phone else page.mouse.click)(w * x, h * y)
                        page.wait_for_timeout(150)
                if game in counts and w < h:
                    # bo giai trong game (dung cho goi y) phai ra dung so buoc it nhat ma tools/carjam.py da ghi;
                    # Boba Sort: bo giai trong game phai giai noi moi man; Tile Trio: moi man doc ra phai du bo ba
                    page.goto(f"{base}/{game}/none/index.html?selftest=1")
                    page.wait_for_function("document.title.startsWith('selftest:')", timeout=60000)
                    _, count, wrong = page.title().split(":")
                    if int(count) != counts[game]:
                        errors.append(f"so man trong game khac levels/{game}.json")
                    if wrong:
                        errors.append(f"tu kiem trong game sai o man {wrong[:40]}")
                ctx.close()
            failed = failed or bool(errors)
            results.append(f"{game}: " + (f"dat, tai {load:.1f} giay" if not errors else "LOI " + " | ".join(dict.fromkeys(errors))))
        browser.close()
    server.shutdown()
    return results, failed


if __name__ == "__main__":
    lines, bad = run()
    print("\n".join(lines))
    sys.exit(1 if bad else 0)
