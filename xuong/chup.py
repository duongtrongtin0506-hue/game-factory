"""Chụp ảnh / kiểm DOM sản phẩm bằng Chrome headless (máy 1, máy 2 hoặc GitHub Actions) – không cần Playwright.
  python xuong/chup.py shot <url|tệp.html> <out.png> <rộng>x<cao> [--dark]
  python xuong/chup.py dom  <url|tệp.html>            -> in DOM sau khi JS chạy (Cửa 0 vòng 1: kiểm JS có chạy)
  python xuong/chup.py gif  <out.gif> <a.png> <b.png> ... [--w 800]   -> GIF demo từ các ảnh chụp (ffmpeg)
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

CANDS = [os.environ.get("CHROME", ""), r"C:\Program Files\Google\Chrome\Application\chrome.exe",
         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "google-chrome", "chromium", "chromium-browser"]


def chrome():
    for c in CANDS:
        if c and (Path(c).exists() or shutil.which(c)):
            return c
    sys.exit("Không thấy Chrome/Edge")


def url(x):
    return x if "://" in x else Path(x.split("#")[0]).resolve().as_uri() + ("#" + x.split("#", 1)[1] if "#" in x else "")


def base(extra):
    prof = tempfile.mkdtemp(prefix="chup-")
    return [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-sandbox",
            "--force-device-scale-factor=1", f"--user-data-dir={prof}", "--virtual-time-budget=4000", *extra]


def shot(src, out, size, dark=False):
    w, h = size.lower().split("x")
    ex = [f"--window-size={w},{h}", f"--screenshot={Path(out).resolve()}"]
    if dark:
        ex.append("--blink-settings=preferredColorScheme=0")
    subprocess.run(base(ex) + [url(src)], capture_output=True, timeout=90)
    return Path(out).exists()


def dom(src):
    r = subprocess.run(base(["--dump-dom"]) + [url(src)], capture_output=True, timeout=90, text=True, encoding="utf-8", errors="ignore")
    return r.stdout


def gif(out, pngs, w=800):
    lst = Path(tempfile.mkdtemp()) / "l.txt"
    lst.write_text("".join(f"file '{Path(p).resolve().as_posix()}'\nduration 1.4\n" for p in pngs) + f"file '{Path(pngs[-1]).resolve().as_posix()}'\n")
    vf = f"scale={w}:-2:flags=lanczos,pad=ceil(iw/2)*2:ceil(ih/2)*2,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", vf, "-loop", "0", str(out)], check=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a[0] == "shot":
        print(shot(a[1], a[2], a[3], "--dark" in a))
    elif a[0] == "dom":
        print(dom(a[1]))
    elif a[0] == "gif":
        w = int(a[a.index("--w") + 1]) if "--w" in a else 800
        gif(a[1], [x for x in a[2:] if x.endswith(".png")], w)
