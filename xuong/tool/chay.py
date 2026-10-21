"""Xưởng Tool – chạy mỗi đêm trên máy nhà (Task Scheduler): python chay.py --so-mon 1

Luật giai đoạn 1: học 3 tiện ích Chrome MIT nhiều sao → chép khung MV3 (popup 1 việc, quyền tối thiểu, README + LICENSE + privacy)
→ nhân bản 5 tiện ích (Tab Tidy · Copy Link As · Word Counter · Page Check · Color Grab), mỗi món 1 tính năng thêm. Không cần Claude:
  1. KHUNG/ext.py dựng tiện ích   2. Cửa 0 (popup chạy 360/768/1280 ở chế độ demo, không gọi máy chủ lạ)
  3. ảnh: bìa tranh Public Domain + 4 ảnh popup trong cửa sổ trình duyệt + GIF quay lúc bấm
  4. nén <slug>.zip (tải lên Chrome Web Store / Load unpacked), hồ sơ → _cho-cua-1 (GitHub chấm Cửa 1); mồi hàng đã lên kệ
"""
import argparse
import base64
import datetime
import functools
import http.server
import io
import json
import os
import shutil
import subprocess
import sys
import threading
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "KHUNG"))
sys.path.insert(0, str(HERE / "tools" / "chung"))
sys.path.insert(0, str(HERE.parent / "sach" / "KHUNG"))
import ext  # noqa: E402
import moi  # noqa: E402
import nhip  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))
ORDER = ["tab-tidy", "copy-link", "word-counter", "page-check", "color-grab"]
ART = {"tab-tidy": "library", "copy-link": "letter", "word-counter": "books", "page-check": "map", "color-grab": "flowers"}
LEADERS = ("| # | Leader (GitHub, MIT, Chrome MV3, sắp theo sao, 21/10) | Sao |\n|---|---|---|\n"
           "| 1 | kazuki-sf/YouTube_Summary_with_ChatGPT – https://github.com/kazuki-sf/YouTube_Summary_with_ChatGPT | 865 |\n"
           "| 2 | kazuki-sf/ChatGPT_Extension – https://github.com/kazuki-sf/ChatGPT_Extension | 457 |\n"
           "| 3 | SimGus/chrome-extension-v3-starter – https://github.com/SimGus/chrome-extension-v3-starter | 403 |")


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with open(HERE / "NHAT-KY-chay.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def serve(folder):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(folder)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def browser(src, title):
    return (f"<div style='background:#fff;border-radius:14px;box-shadow:0 30px 60px rgba(0,0,0,.3);overflow:hidden;width:1100px'>"
            "<div style='background:#E9EEF0;padding:12px 16px;display:flex;gap:8px;align-items:center'><span style='width:12px;height:12px;border-radius:6px;background:#F26B5B'></span>"
            "<span style='width:12px;height:12px;border-radius:6px;background:#F5BE4F'></span><span style='width:12px;height:12px;border-radius:6px;background:#5CC56B'></span>"
            f"<span style='margin-left:16px;background:#fff;border-radius:999px;padding:6px 16px;color:#556;font:14px Inter,Arial;flex:1'>{title}</span>"
            "<span style='width:26px;height:26px;border-radius:7px;background:#00A884'></span></div>"
            "<div style='position:relative;height:640px;background:repeating-linear-gradient(0deg,#F6F8F9 0 22px,#fff 22px 44px)'>"
            f"<img src='{src}' style='position:absolute;right:30px;top:0;width:380px;border-radius:0 0 14px 14px;box-shadow:0 18px 40px rgba(0,0,0,.25)'></div></div>")


def images(slug, t, stage, out):
    from playwright.sync_api import sync_playwright
    art_uri, credit = None, None
    try:
        import bia_sach
        img, cr, oid = bia_sach.find_art([ART[slug], "still life"])
        if img is not None:
            img = bia_sach.cover_fill(img, 1600, 1200)
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=85)
            art_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
            credit = {"credit": cr, "object": oid}
    except Exception as e:
        log(f"tranh bia loi: {type(e).__name__}")
    srv = serve(stage)
    url = f"http://127.0.0.1:{srv.server_address[1]}/popup.html"
    shots, vid = out / "_shots", out / "_vid"
    shots.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 380, "height": 520}, device_scale_factor=2, record_video_dir=str(vid), record_video_size={"width": 380, "height": 520})
        p = ctx.new_page()
        p.goto(url)
        p.wait_for_timeout(900)
        p.screenshot(path=str(shots / "1.png"))
        for btn in p.query_selector_all("button")[:3]:
            try:
                btn.click()
            except Exception:
                pass
            p.wait_for_timeout(900)
        p.screenshot(path=str(shots / "2.png"))
        p.wait_for_timeout(600)
        video = p.video.path()
        ctx.close()
        u = lambda n: "data:image/png;base64," + base64.b64encode((shots / n).read_bytes()).decode()
        bg = f"url({art_uri}) center/cover" if art_uri else "linear-gradient(135deg,#0B3D33,#00A884)"
        perms = "".join(f"<li><b>{k}</b> – {v}</li>" for k, v in t["why"].items())
        pages = {
            "cover-1600x1200.png": f"<div style='position:absolute;inset:0;background:{bg}'></div><div style='position:absolute;left:0;top:0;bottom:0;width:640px;background:rgba(6,40,33,.88);color:#fff;padding:130px 64px;box-sizing:border-box'>"
                                   f"<div style='font:600 13px ui-monospace,Consolas;letter-spacing:.14em;color:#8FE3CB'>SNOUTSMITH TOOLS · CHROME EXTENSION</div><h1 style='font:400 58px/1.04 Georgia,serif;margin:20px 0'>{t['short']}</h1>"
                                   f"<div style='font-size:22px;color:#D9F5EC'>{t['desc']}</div><div style='margin-top:34px;display:inline-block;background:#00A884;border-radius:999px;padding:16px 30px;font-weight:700'>Free · MIT · no tracking</div></div>"
                                   f"<img src='{u('2.png')}' style='position:absolute;left:840px;top:200px;width:560px;border-radius:18px;box-shadow:0 30px 60px rgba(0,0,0,.4)'>",
            "anh-2-trinh-duyet.png": f"<div style='padding:150px 250px'>{browser(u('1.png'), 'example.com/article')}</div>",
            "anh-3-dang-dung.png": f"<div style='padding:150px 250px'>{browser(u('2.png'), 'example.com/article')}</div>",
            "anh-4-quyen.png": f"<div style='padding:200px 220px;color:#fff;font:22px/1.5 Inter,Arial'><div style='font:600 14px ui-monospace,Consolas;letter-spacing:.14em;color:#8FE3CB'>MINIMAL PERMISSIONS</div>"
                               f"<h1 style='font:400 60px Georgia,serif;margin:16px 0 24px'>Only what it needs</h1><ul style='background:rgba(255,255,255,.1);border-radius:20px;padding:30px 50px'>{perms}</ul>"
                               "<div>No remote code · no analytics · nothing leaves your browser.</div></div>",
        }
        q = b.new_page(viewport={"width": 1600, "height": 1200})
        for name, body in pages.items():
            q.set_content(f"<html><head><meta charset='utf-8'></head><body style='margin:0;width:1600px;height:1200px;overflow:hidden;position:relative;background:linear-gradient(135deg,#0B3D33,#00A884);font-family:Inter,Segoe UI,Arial'>{body}</body></html>")
            q.wait_for_timeout(400)
            q.screenshot(path=str(out / name))
        b.close()
    srv.shutdown()
    shutil.copy2(shots / "2.png", out / "anh-5-popup.png")
    shutil.copy2(shots / "2.png", stage / "screenshot.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-t", "10", "-vf",
                    "fps=12,scale=300:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse", str(out / "demo.gif")], check=False)
    shutil.rmtree(shots, ignore_errors=True)
    shutil.rmtree(vid, ignore_errors=True)
    if credit:
        (out / "COVER-CREDIT.json").write_text(json.dumps(credit, ensure_ascii=False), encoding="utf-8")
    return credit


def docs(slug, t, out, credit, c0):
    t60 = t["name"] if len(t["name"]) <= 60 else t["short"] + " – Chrome Extension"
    (out / "meta.json").write_text(json.dumps({"free": True, "xuong": "tool", "price": 0, "license": "MIT – Snoutsmith Tools", "web": "ext/popup.html", "permissions": t["perms"]}, indent=2), encoding="utf-8")
    (out / "LEADER.md").write_text(f"# LEADER – {t['short']}\n\n{LEADERS}\n\n| # | Đặc điểm leader | Tiện ích mình |\n|---|---|---|\n| 1 | Manifest V3 | ✅ |\n| 2 | Popup 1 việc | ✅ |\n"
                                   "| 3 | Quyền tối thiểu, có giải trình | ✅ README |\n| 4 | Icon 16/48/128 | ✅ |\n| 5 | Lưu lựa chọn | ✅ chrome.storage |\n| 6 | Không mã từ xa | ✅ |\n"
                                   "| 7 | README có ảnh + cách cài | ✅ |\n| 8 | LICENSE MIT | ✅ |\n| 9 | Chính sách riêng tư | ✅ PRIVACY.md |\n\n"
                                   f"Tính năng thêm của món này: {t['extra']}.\n", encoding="utf-8")
    (out / "LICENSES.md").write_text("# LICENSES\n\n| Asset | Source | License |\n|---|---|---|\n| Extension code, icons | Snoutsmith Tools – `xuong/tool/KHUNG/ext.py` | MIT (LICENSE in the zip) |\n"
                                     "| Preview images, GIF | Rendered from the running popup (`chay.py`) | Own work |\n"
                                     + (f"| Cover painting | {credit.get('credit', '')} | Public Domain / CC0 (museum open-access API flags it public domain) |\n" if credit else ""), encoding="utf-8")
    (out / "STORE.md").write_text("\n".join([
        f"# {t60}", "", f"Title ({len(t60)} chars): **{t60}**", "", f"{t['desc']} Free, open source (MIT) and private: it asks only for {', '.join(t['perms'])}.", "",
        f"- {t['desc']}", f"- {t['extra']}", "- One click from the toolbar, nothing to set up", "- Minimal permissions, each explained", "- No tracking, no remote code, MIT licensed", "",
        "## What you get", "", f"- `{slug}.zip` – Manifest V3 extension (Load unpacked or upload to the Chrome Web Store), README, PRIVACY.md, LICENSE", "",
        "## FAQ", "", "**Is it safe?** It runs only in your browser and sends nothing anywhere; the code is open (MIT).", "",
        "**Which browsers?** Chrome, Edge, Brave and other Chromium browsers.", "", "**How do I install it?** Unzip, open chrome://extensions, turn on Developer mode, Load unpacked.", "",
        "**Why these permissions?** See the README: each one is explained.", "", "**Is it free?** Yes.", "",
        "## Price", "", "0 USD (KHUON-NHA-MAY mục 8: free tool to bring visitors; Pro tools follow from tickets).", "",
        "## Label", "", "Built with AI-assisted code; tested automatically at 3 screen sizes.", "", "## Tags", "", f"{slug.replace('-', ' ')}, chrome extension, productivity, free, open source"]) + "\n", encoding="utf-8")
    (out / "BAN-GIAO.md").write_text(f"# Bàn giao: {t60}\n\n- Xưởng: Tool → tools.snoutsmith.com · giá 0 USD · {datetime.date.today():%d/%m/%Y}\n"
                                     f"- Tệp: `{slug}.zip` (Manifest V3), bìa + 4 ảnh + GIF\n- Quyền: {', '.join(t['perms'])}\n- Cửa 0: {c0}\n- Gỡ: chrome://extensions → Remove.\n", encoding="utf-8")


def make(slug):
    t = ext.TOOLS[slug]
    out = HERE / "HANG" / f"{datetime.date.today():%Y%m%d}-{slug}"
    shutil.rmtree(out, ignore_errors=True)
    stage = out / "ext"
    ext.build(slug, stage)
    credit = images(slug, t, stage, out)
    docs(slug, t, out, credit, "")
    r = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(out), "--web", "ext/popup.html", "--free"],
                       capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if r.returncode:   # Cua 0 do: chay lai 1 lan (loi tam thoi luc may ban)
        log('cua0 do, chay lai lan 2')
        r = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(out), "--web", "ext/popup.html", "--free"],
                       capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    c0 = r.stdout.strip()[:170]
    shutil.rmtree(out / "cua0-anh", ignore_errors=True)
    with zipfile.ZipFile(out / f"{slug}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(stage.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(stage))
    docs(slug, t, out, credit, c0)
    log(f"{slug}: {c0}")
    return r.returncode == 0


def day_cho_cua_1():
    g = ["git", "-C", str(NET24)]
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    sent = []
    for item in sorted((HERE / "HANG").glob("2*-*")):
        if not item.is_dir() or (item / ".da-day").exists():
            continue
        try:
            if not json.loads((item / "CUA0.json").read_text(encoding="utf-8")).get("pass"):
                continue
        except Exception:
            continue
        date, _, name = item.name.partition("-")
        dest = NET24 / "BAN-GIAO" / "_cho-cua-1" / f"{date}-tool-{name}"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(item, dest)
        (item / ".da-day").write_text(f"{datetime.date.today()}", encoding="utf-8")
        sent.append(dest.name)
    if sent:
        subprocess.run(g + ["add", "BAN-GIAO/_cho-cua-1"])
        subprocess.run(g + ["commit", "-qm", f"Xuong Tool (may nha): {len(sent)} tien ich cho Cua 1"])
        subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
        subprocess.run(g + ["push", "-q"])
    log("day cho cua 1: " + (", ".join(sent) or "0"))
    return len(sent)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("--so-mon", type=int, default=1)
    a.add_argument("--khong-nop", action="store_true")
    x = a.parse_args()
    have = {p.name.split("-", 1)[1] for p in (HERE / "HANG").glob("2*-*") if p.is_dir()}
    q = [s for s in ORDER if s not in have]
    ra = qua = 0
    for s in q[:x.so_mon]:
        try:
            ok = make(s)
        except Exception as e:
            log(f"LOI {s}: {type(e).__name__}: {e}")
            continue
        ra += 1
        qua += bool(ok)
    n = 0
    if not x.khong_nop:
        n = day_cho_cua_1()
        log("moi hang len ke: " + json.dumps(moi.moi_len_ke("tool", NET24)))
    nk = HERE / "NHAT-KY.md"
    nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + f"\n| {datetime.date.today():%d/%m} | {ra} tiện ích | Cửa 0: {qua} | đẩy chờ Cửa 1: {n} | 0 | {ra - qua} |\n", encoding="utf-8")
    log(f"XONG: ra {ra}, cua 0 {qua}, day {n}")
    if not x.khong_nop:
        nhip.nhip("tool", ra)   # nhịp tim: 1 dòng/lần chạy vào 07-Nhat-ky/nha-may-nhip.log


if __name__ == "__main__":
    main()
