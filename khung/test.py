"""Automatic check + store media for every Drop & Merge game: python khung/test.py [variant-id] [--fast]

Per game (serves khung/dist on a local port, Chromium via Playwright):
  1. selftest: every level's stored solution replayed in the page (title selftest:0)
  2. load on phone portrait 360x640, phone landscape 640x360, desktop 1280x720: no console error, load time
  3. autoplay: the solver plays levels 1-10 in a 360x640 window, video recorded, FPS sampled every second
  4. covers 512x512, 512x384, 1280x720 (+ 1920x1080), three 1280x720 / 720x1280 screenshots, 5 s GIF
Writes khung/proof/<id>/ (report.json, video, images) and khung/proof/REPORT.md.
"""
import functools
import http.server
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

K = Path(__file__).resolve().parent
PORT = 8977
FAST = "--fast" in sys.argv


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=str(K))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def url(vid, q=""):
    return f"http://127.0.0.1:{PORT}/dist/{vid}/index.html?{q}"


def check(browser, vid, out):
    rep = {"id": vid, "errors": [], "loads": {}}
    # 1. selftest
    p = browser.new_page()
    p.on("console", lambda m: rep["errors"].append(m.text) if m.type == "error" else None)
    p.on("pageerror", lambda e: rep["errors"].append(str(e)))
    p.goto(url(vid, "selftest=1&fresh=1"))
    p.wait_for_function("document.title.startsWith('selftest:')", timeout=120000)
    rep["selftest"] = p.title()
    p.close()
    # 2. sizes + load time (slow 4G-like CPU throttle on the phone sizes)
    for name, (w, h) in {"phone-portrait-360x640": (360, 640), "phone-landscape-640x360": (640, 360), "desktop-1280x720": (1280, 720)}.items():
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 700 else 1)
        p = ctx.new_page()
        p.on("console", lambda m: rep["errors"].append(f"{name}: {m.text}") if m.type == "error" else None)
        p.on("pageerror", lambda e: rep["errors"].append(f"{name}: {e}"))
        if w < 700:
            cdp = ctx.new_cdp_session(p)
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6e6 / 8 * 4, "uploadThroughput": 750e3 / 8})
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        t0 = time.time()
        p.goto(url(vid, "fresh=1"), wait_until="load")
        p.wait_for_timeout(600)
        rep["loads"][name] = round(time.time() - t0, 2)
        p.screenshot(path=str(out / f"size-{name}.png"))
        p.mouse.click(w / 2, h * 0.72 if w < h else h * 0.82)   # Play
        p.wait_for_timeout(400)
        p.screenshot(path=str(out / f"size-{name}-play.png"))
        ctx.close()
    # 3. autoplay 10 levels with video + FPS
    vdir = out / "_video"
    shutil.rmtree(vdir, ignore_errors=True)
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, record_video_dir=str(vdir), record_video_size={"width": 360, "height": 640})
    p = ctx.new_page()
    p.on("console", lambda m: rep["errors"].append(f"autoplay: {m.text}") if m.type == "error" else None)
    p.on("pageerror", lambda e: rep["errors"].append(f"autoplay: {e}"))
    levels = 3 if FAST else 10
    p.goto(url(vid, f"autoplay={levels}&speed=2.5&fresh=1"))
    samples = []
    for _ in range(600):
        p.wait_for_timeout(1000)
        st = p.evaluate("({done: window.__auto.done, won: window.__auto.won, lost: window.__auto.lost, fps: window.__fps.now})")
        samples.append(round(st["fps"], 1))
        if st["done"]:
            break
    rep["autoplay"] = {"levels": levels, "won": st["won"], "lost": st["lost"], "seconds": len(samples)}
    s = sorted(samples[2:]) or [0]
    rep["fps"] = {"median": s[len(s) // 2], "p10": s[len(s) // 10], "samples": len(samples)}
    video = p.video.path()
    ctx.close()
    dest = out / f"autoplay-{levels}-levels.webm"
    shutil.move(video, dest)
    shutil.rmtree(vdir, ignore_errors=True)
    rep["video"] = dest.name
    # 4. store media
    for w, h in ((512, 512), (512, 384), (1280, 720), (1920, 1080), (720, 1280)):
        p = browser.new_page(viewport={"width": w, "height": h})
        p.goto(url(vid, f"cover=1&w={w}&h={h}"))
        p.wait_for_timeout(300)
        p.screenshot(path=str(out / f"cover-{w}x{h}.png"))
        p.close()
    shots = [("shot-1-menu", "fresh=1"), ("shot-2-level", "fresh=1&level=6"), ("shot-3-level", "fresh=1&level=24")]
    for name, q in shots:
        for w, h in ((1280, 720), (720, 1280)):
            p = browser.new_page(viewport={"width": w, "height": h})
            p.goto(url(vid, q))
            p.wait_for_timeout(400)
            if "level" in q:   # one drop so the board shows a merge in progress state
                p.evaluate("dropAt(Engine.bestColumn(P.lv, P.run, P.list))")
                p.wait_for_timeout(900)
            p.screenshot(path=str(out / f"{name}-{w}x{h}.png"))
            p.close()
    # GIF 5 s from the autoplay video (seconds 2-7), 360 px wide
    gif = out / "preview-5s.gif"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2", "-t", "5", "-i", str(dest),
                    "-vf", "fps=12,scale=270:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse", str(gif)], check=False)
    mp4 = out / "trailer.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dest), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", str(mp4)], check=False)
    rep["zip_kb"] = {z.name: round(z.stat().st_size / 1024) for z in sorted((K / "dist" / vid).glob("*.zip"))}
    ok_load = all(v < 3 for v in rep["loads"].values())
    rep["pass"] = (rep["selftest"].startswith("selftest:0") and not rep["errors"] and not st["lost"] and len(st["won"]) == levels
                   and ok_load and rep["fps"]["median"] >= 55)
    (out / "report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return rep


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    variants = [v["id"] for v in json.loads((K / "variants.json").read_text(encoding="utf-8")) if not only or v["id"] in only]
    srv = serve()
    reps = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for vid in variants:
            out = K / "proof" / vid
            out.mkdir(parents=True, exist_ok=True)
            r = check(browser, vid, out)
            print(vid, "PASS" if r["pass"] else "FAIL", r["selftest"], "fps", r["fps"], "won", r["autoplay"]["won"], "errors", r["errors"][:3], "loads", r["loads"])
            reps.append(r)
        browser.close()
    srv.shutdown()
    lines = ["# Drop & Merge â€“ automatic test report", "", f"Run: {time.strftime('%Y-%m-%d %H:%M')} Â· Chromium (Playwright) Â· {'fast' if FAST else 'full'}", "",
             "| Game | Result | Selftest (all levels) | Autoplay won | FPS median / p10 | Load s (360p Â· 640l Â· 1280) | Console errors | Zip KB (largest) |",
             "|---|---|---|---|---|---|---|---|"]
    for r in reps:
        lines.append(f"| {r['id']} | {'PASS' if r['pass'] else 'FAIL'} | {r['selftest']} | {len(r['autoplay']['won'])}/{r['autoplay']['levels']} | "
                     f"{r['fps']['median']} / {r['fps']['p10']} | {' Â· '.join(str(v) for v in r['loads'].values())} | {len(r['errors'])} | {max(r['zip_kb'].values())} |")
    lines += ["", "Phone sizes load with 4x CPU throttle and a 150 ms / 6.4 Mbps network (4G-like). FPS sampled each second while the solver plays.", ""]
    (K / "proof" / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    sys.exit(0 if all(r["pass"] for r in reps) else 1)


if __name__ == "__main__":
    main()
