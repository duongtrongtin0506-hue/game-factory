# -*- coding: utf-8 -*-
"""Chup anh bia va quay video xem truoc cua mot game bang chinh che do ?demo= cua game do:
  python tools/quay.py car-jam            anh bia moi co + 2 video
  python tools/quay.py car-jam --no-video chi anh bia
Game ve tung khung hinh roi gui POST /frame ve may chu nho trong tep nay (chi nghe 127.0.0.1).
Ket qua: assets-goc/<game>/ (anh co trong git, video thi khong) va chep sang dist/<game>/assets/.
Video can ffmpeg trong PATH; khong co thi bo qua video va bao."""
import functools
import http.server
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# (rong, cao, duoi): CrazyGames 1920x1080 / 800x1200 / 800x800 lay tu ban lon; GameMonetize 512x*; Playgama 800x800, 1080x1920, 1920x1080; Yandex 800x470; GameDistribution 512x384, 512x512, 200x120, 1280x720, 1280x550 (jpg)
COVERS = [(2880, 1620, "png"), (1200, 1800, "png"), (800, 1200, "png"), (1200, 1200, "png"), (1920, 1080, "png"), (1080, 1920, "png"), (800, 800, "png"),
          (800, 470, "png"), (512, 512, "jpg"), (512, 384, "jpg"), (512, 340, "jpg"),
          (1280, 720, "jpg"), (1280, 550, "jpg"), (200, 120, "jpg")]
VIDEOS = [("landscape", 1920, 1080), ("portrait", 1080, 1620)]
frames, done = {}, threading.Event()


class Capture(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        q = parse_qs(urlparse(self.path).query)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if q.get("n", [""])[0] == "done":
            done.set()
        else:
            frames[q["n"][0]] = body
        self.send_response(204)
        self.end_headers()


def shoot(page, url, w, h, timeout):
    frames.clear()
    done.clear()
    page.set_viewport_size({"width": w, "height": h})
    page.goto(url)
    if not done.wait(timeout):
        raise SystemExit(f"het gio cho game ve xong: {url}")
    return dict(frames)


def main():
    game = sys.argv[1]
    out = ROOT / "assets-goc" / game
    out.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Capture, directory=str(ROOT / "dist")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/{game}/none/index.html"
    made = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("pageerror", lambda e: print("js:", str(e)[:200]))
        for w, h, ext in COVERS:
            png = shoot(page, f"{base}?demo=cover&w={w}&h={h}", w, h, 60)["cover"]
            target = out / f"cover-{w}x{h}.{ext}"
            if ext == "png":
                target.write_bytes(png)
            else:   # trinh duyet doi PNG sang JPEG, khong can thu vien anh
                page.set_content("<canvas id=c></canvas>")
                target.write_bytes(bytes(page.evaluate("""async (d) => { const img = new Image(); img.src = 'data:image/png;base64,' + d; await img.decode();
                  const c = document.getElementById('c'); c.width = img.width; c.height = img.height; c.getContext('2d').drawImage(img, 0, 0);
                  const b = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.9)); return Array.from(new Uint8Array(await b.arrayBuffer())); }""",
                                                       __import__("base64").b64encode(png).decode())))
            made.append(target.name)
        if "--no-video" not in sys.argv:
            if not ffmpeg:
                print("khong co ffmpeg: bo qua video")
            for name, w, h in VIDEOS if ffmpeg else []:
                got = shoot(page, f"{base}?demo={name}&w={w}&h={h}", w, h, 600)
                with tempfile.TemporaryDirectory() as tmp:
                    for i, key in enumerate(sorted(got)):
                        (Path(tmp) / f"f{i:04d}.jpg").write_bytes(got[key])
                    target = out / f"preview-{name}-{w}x{h}.mp4"
                    run = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", "30", "-i", str(Path(tmp) / "f%04d.jpg"),
                                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(target)], capture_output=True)
                    if run.returncode:
                        raise SystemExit("ffmpeg: " + run.stderr.decode("utf-8", "replace")[-300:])
                made.append(f"{target.name} ({len(got)} khung)")
        browser.close()
    server.shutdown()
    dist = ROOT / "dist" / game / "assets"
    dist.mkdir(parents=True, exist_ok=True)
    for f in out.iterdir():
        shutil.copy2(f, dist / f.name)
    print(f"{game}: " + ", ".join(made))


if __name__ == "__main__":
    main()
