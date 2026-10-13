# -*- coding: utf-8 -*-
"""Chup nhanh cac man hinh cua mot game de soat giao dien (THIET-KE.md, thu nhin xa):
  python tools/chup.py boba-sort "" "?level=3" "?level=5&win=1"      -> _build/anh/<game>-<so>.png (ghep 1 hang, co dien thoai)
  them --ngang de chup co 844x390. Dung ban dist/<game>/none (chay tools/build.py truoc)."""
import functools
import http.server
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    game, paths = args[0], args[1:] or [""]
    w, h = (844, 390) if "--ngang" in sys.argv else (390, 844)
    out = ROOT / "_build" / "anh"
    out.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT / "dist")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/{game}/none/index.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w * len(paths), "height": h})
        frames = "".join(f'<iframe src="{base}{q}" style="width:{w}px;height:{h}px;border:0;float:left"></iframe>' for q in paths)
        page.set_content(f'<body style="margin:0">{frames}</body>')
        page.wait_for_timeout(2500)
        target = out / f"{game}{'-ngang' if w > h else ''}.png"
        page.screenshot(path=str(target))
        browser.close()
    server.shutdown()
    print(target)


if __name__ == "__main__":
    main()
