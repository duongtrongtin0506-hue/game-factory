"""Xưởng App – chạy mỗi đêm trên máy nhà (Task Scheduler): python chay.py --so-mon 1

Luật giai đoạn 1: học 3 PWA MIT nhiều sao → chép khung (1 màn nhập → kết quả → offline → cài được) → nhân bản 5 app
(Lãi kép · Trả góp · Chia hóa đơn/tip · Đổi đơn vị · Pomodoro). Không cần Claude:
  1. KHUNG/pwa.py dựng app (manifest, service worker, icon, privacy, twa-manifest Bubblewrap)
  2. Cửa 0 --pwa: 360/768/1280 không lỗi, mở được khi mất mạng, không gọi máy chủ lạ
  3. ảnh: bìa tranh Public Domain + 4 ảnh mockup + GIF quay lúc gõ số
  4. nén <slug>.zip, hồ sơ → đẩy net24-he-thong/BAN-GIAO/_cho-cua-1/ (GitHub chấm Cửa 1); mồi hàng đã lên kệ
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
import moi  # noqa: E402
import pwa  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Desktop\net24-he-thong"))
ORDER = ["compound-interest", "loan-payment", "tip-split", "unit-converter", "pomodoro-timer"]
ART = {"compound-interest": "harvest", "loan-payment": "house", "tip-split": "dinner", "unit-converter": "map", "pomodoro-timer": "clock"}
TRY = {"compound-interest": [("p", "25000"), ("m", "500"), ("y", "20")], "loan-payment": [("a", "32000"), ("r", "6.2"), ("y", "4")],
       "tip-split": [("b", "142.80"), ("t", "20"), ("n", "5")], "unit-converter": [("x", "42"), ("x", "100"), ("x", "5")], "pomodoro-timer": [("f", "50"), ("s", "10"), ("k", "3")]}
LEADERS = ("| # | Leader (GitHub, MIT, sắp theo sao, 21/10) | Sao |\n|---|---|---|\n| 1 | cocopon/llumino-pwa – https://github.com/cocopon/llumino-pwa | 94 |\n"
           "| 2 | ovk/clcalc – https://github.com/ovk/clcalc | 46 |\n| 3 | chrisdiana/pwa-calculator – https://github.com/chrisdiana/pwa-calculator | 33 |")


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


def phone(src, label, bg):
    return (f"<div style='display:flex;flex-direction:column;align-items:center;gap:22px'><div style='background:#111;border-radius:52px;padding:16px;width:380px;height:780px;box-shadow:0 30px 60px rgba(0,0,0,.35)'>"
            f"<img src='{src}' style='width:100%;height:100%;object-fit:cover;object-position:top;border-radius:38px'></div><div style='color:#fff;font:600 20px Inter,Arial'>{label}</div></div>")


def images(slug, app, stage, out):
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
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    shots, vid = out / "_shots", out / "_vid"
    shots.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, record_video_dir=str(vid), record_video_size={"width": 390, "height": 844})
        p = ctx.new_page()
        p.goto(url)
        p.wait_for_timeout(900)
        p.screenshot(path=str(shots / "1.png"))
        for i, (k, v) in enumerate(TRY[slug]):
            p.fill("#" + k, "")
            p.type("#" + k, v, delay=120)
            p.wait_for_timeout(700)
            if i == 0:
                p.screenshot(path=str(shots / "2.png"))
        p.evaluate("window.scrollTo(0, 420)")
        p.wait_for_timeout(600)
        p.screenshot(path=str(shots / "3.png"))
        p.wait_for_timeout(800)
        video = p.video.path()
        ctx.close()
        d = b.new_page(viewport={"width": 1280, "height": 800})
        d.goto(url)
        d.wait_for_timeout(700)
        d.screenshot(path=str(shots / "desk.png"))
        d.close()
        u = lambda n: "data:image/png;base64," + base64.b64encode((shots / n).read_bytes()).decode()   # set_content pages cannot read file://
        bg = f"url({art_uri}) center/cover" if art_uri else "linear-gradient(135deg,#2A1B5C,#7A4DE8)"
        pages = {
            "cover-1600x1200.png": f"<div style='position:absolute;inset:0;background:{bg}'></div><div style='position:absolute;left:0;top:0;bottom:0;width:640px;background:rgba(30,18,64,.86);color:#fff;padding:130px 64px;box-sizing:border-box'>"
                                   f"<div style='font:600 13px ui-monospace,Consolas;letter-spacing:.14em;color:#C9B6FF'>SNOUTSMITH APPS · INSTALLS LIKE AN APP</div><h1 style='font:400 62px/1.02 Georgia,serif;margin:20px 0'>{app['name']}</h1>"
                                   f"<div style='font-size:21px;color:#E5DDFF'>{app['desc']}</div><div style='margin-top:34px;display:inline-block;background:#7A4DE8;border-radius:999px;padding:16px 30px;font-weight:700'>Free · offline · no ads</div></div>"
                                   f"<div style='position:absolute;left:820px;top:150px'>{phone(u('2.png'), '', '')}</div>",
            "anh-2-dien-thoai.png": f"<div style='display:flex;gap:70px;justify-content:center;padding-top:120px'>{phone(u('1.png'), 'Type your numbers', '')}{phone(u('3.png'), 'Get the answer instantly', '')}</div>",
            "anh-3-may-tinh.png": f"<div style='padding:110px 140px'><div style='background:#111;border-radius:22px 22px 0 0;padding:20px'><img src='{u('desk.png')}' style='width:100%;border-radius:6px;display:block'></div><div style='height:26px;background:linear-gradient(#ddd,#b9b9c0);border-radius:0 0 28px 28px;margin:0 -40px'></div><div style='color:#fff;font:600 22px Inter,Arial;margin-top:28px;text-align:center'>Same app on your laptop</div></div>",
            "anh-4-offline.png": "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:28px;padding:220px 120px'>" + "".join(
                f"<div style='background:#fff;border-radius:24px;padding:40px;font:400 20px Inter,Arial;color:#1A1A2E'><div style='font:600 52px Georgia,serif;color:#7A4DE8'>{t}</div><div style='font-weight:700;margin:14px 0 8px'>{h}</div>{x}</div>"
                for t, h, x in [("↓", "Install", "Add to your home screen from the browser – it opens like an app."), ("✈", "Offline", "Works with no signal once opened; nothing to download later."),
                                ("🔒", "Private", "No account, no ads, no trackers. Your numbers stay on your device.")]) + "</div>",
        }
        q = b.new_page(viewport={"width": 1600, "height": 1200})
        for name, body in pages.items():
            q.set_content(f"<html><head><meta charset='utf-8'></head><body style='margin:0;width:1600px;height:1200px;overflow:hidden;position:relative;background:linear-gradient(135deg,#2A1B5C,#7A4DE8);font-family:Inter,Segoe UI,Arial'>{body}</body></html>")
            q.wait_for_timeout(400)
            q.screenshot(path=str(out / name))
        b.close()
    srv.shutdown()
    shutil.copy2(shots / "2.png", out / "anh-5-man-hinh-390.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-t", "10", "-vf",
                    "fps=12,scale=300:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse", str(out / "demo.gif")], check=False)
    shutil.rmtree(shots, ignore_errors=True)
    shutil.rmtree(vid, ignore_errors=True)
    if credit:
        (out / "COVER-CREDIT.json").write_text(json.dumps(credit, ensure_ascii=False), encoding="utf-8")
    return credit


def docs(slug, app, info, out, credit, c0):
    t60 = app["name"] + " – Offline App"
    (out / "meta.json").write_text(json.dumps({"free": True, "xuong": "app", "price": 0, "license": "MIT – Snoutsmith Apps", "web": "app/index.html", "kb_code": info["kb_code"]}, indent=2), encoding="utf-8")
    (out / "LEADER.md").write_text(f"# LEADER – {app['name']}\n\n{LEADERS}\n\n| # | Đặc điểm leader | App mình |\n|---|---|---|\n"
                                   "| 1 | Một màn, kết quả tức thì | ✅ |\n| 2 | manifest + icon | ✅ 192/512 maskable |\n| 3 | Chạy offline (service worker) | ✅ Cửa 0 kiểm khi mất mạng |\n"
                                   "| 4 | Cài được | ✅ nút Install |\n| 5 | Mobile trước | ✅ 360/768/1280 không tràn |\n| 6 | Nhớ lần nhập | ✅ localStorage |\n"
                                   "| 7 | Không theo dõi | ✅ trang privacy |\n| 8 | Nhẹ, không framework | ✅ " + str(info["kb_code"]) + " KB mã |\n| 9 | Sáng/tối | ✅ theo máy |\n\n"
                                   "Thêm so với leader: twa-manifest.json sẵn cho Bubblewrap (Google Play), bảng kết quả chi tiết.\n", encoding="utf-8")
    (out / "LICENSES.md").write_text("# LICENSES\n\n| Asset | Source | License |\n|---|---|---|\n| App code (HTML/CSS/JS), icons | Snoutsmith Apps – `xuong/app/KHUNG/pwa.py` | MIT (LICENSE in the zip) |\n"
                                     "| Fonts | System fonts only | – |\n| Preview images, GIF | Rendered from the running app (`chay.py`) | Own work |\n"
                                     + (f"| Cover painting | {credit.get('credit', '')} | Public Domain / CC0 (museum open-access API flags it public domain) |\n" if credit else ""), encoding="utf-8")
    (out / "STORE.md").write_text("\n".join([
        f"# {t60}", "", f"Title ({len(t60)} chars): **{t60}**", "", f"{app['desc']} Add it to your home screen and it opens like a native app.", "",
        "- Results update as you type – no Calculate button", "- Works offline after the first visit", "- Remembers your last numbers on your device",
        "- No account, no ads, no trackers", "- Light and dark mode, phone or laptop", "",
        "## What you get", "", f"- `{slug}.zip` – the full app (index.html, app.js, style.css, manifest, service worker, icons, privacy page, MIT license)",
        "- Ready-made `twa-manifest.json` for publishing to Google Play with Bubblewrap", "",
        "## FAQ", "", "**Do I need to install anything?** No. Open it in the browser; installing is optional.", "",
        "**Does it work without internet?** Yes, after it has opened once.", "", "**Is my data uploaded?** No, nothing leaves your device.", "",
        "**Is it financial advice?** No. It shows math only." if slug in ("compound-interest", "loan-payment") else "**Can I share it?** Yes, it is free and MIT-licensed.", "",
        "**Can I host it on my own site?** Yes, the MIT license allows it.", "",
        "## Price", "", "0 USD (lead magnet; a Pro version with export and scenarios can follow – phiếu 20261019-app-pwa-calculator).", "",
        "## Label", "", "Built with AI-assisted code; tested automatically (3 screen sizes + offline).", "", "## Tags", "", f"{slug.replace('-', ' ')}, pwa, offline app, calculator, free"]) + "\n", encoding="utf-8")
    (out / "BAN-GIAO.md").write_text(f"# Bàn giao: {t60}\n\n- Xưởng: App → apps.snoutsmith.com/{slug}/ · giá 0 USD · {datetime.date.today():%d/%m/%Y}\n"
                                     f"- Tệp: `{slug}.zip` (giải nén vào thư mục `/{slug}/` của shop), bìa + 4 ảnh + GIF\n- Cửa 0: {c0}\n"
                                     "- Gỡ: xóa thư mục; trên máy khách không lưu gì ngoài ô nhập lần trước.\n", encoding="utf-8")


def make(slug):
    app = pwa.APPS[slug]
    out = HERE / "HANG" / f"{datetime.date.today():%Y%m%d}-{slug}"
    shutil.rmtree(out, ignore_errors=True)
    stage = out / "app"
    info = pwa.build(slug, stage)
    credit = images(slug, app, stage, out)
    docs(slug, app, info, out, credit, "")
    r = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(out), "--web", "app/index.html", "--free", "--pwa"],
                       capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    c0 = r.stdout.strip()[:170]
    shutil.rmtree(out / "cua0-anh", ignore_errors=True)
    with zipfile.ZipFile(out / f"{slug}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(stage.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(stage))
    docs(slug, app, info, out, credit, c0)
    log(f"{slug}: {info['kb_code']} KB ma, {c0}")
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
        dest = NET24 / "BAN-GIAO" / "_cho-cua-1" / f"{date}-app-{name}"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(item, dest)
        (item / ".da-day").write_text(f"{datetime.date.today()}", encoding="utf-8")
        sent.append(dest.name)
    if sent:
        subprocess.run(g + ["add", "BAN-GIAO/_cho-cua-1"])
        subprocess.run(g + ["commit", "-qm", f"Xuong App (may nha): {len(sent)} app cho Cua 1"])
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
        log("moi hang len ke: " + json.dumps(moi.moi_len_ke("app", NET24)))
    nk = HERE / "NHAT-KY.md"
    nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + f"\n| {datetime.date.today():%d/%m} | {ra} app | Cửa 0: {qua} | đẩy chờ Cửa 1: {n} | 0 | {ra - qua} |\n", encoding="utf-8")
    log(f"XONG: ra {ra}, cua 0 {qua}, day {n}")


if __name__ == "__main__":
    main()
