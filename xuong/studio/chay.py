"""Xưởng Studio – chạy mỗi đêm trên máy nhà (Task Scheduler): python chay.py --so-mon 1

Luật giai đoạn 1: học gói CC0 tải nhiều (Kenney) → chép cấu trúc gói (PNG + spritesheet + JSON + xem trước + demo + LICENSE)
→ nhân bản 6 chủ đề (platformer, puzzle, ui, space, tiles, icons). Không cần Claude:
  1. KHUNG/goi.py gom 3 gói Kenney/chủ đề (kiểm license.txt = CC0, không CC0 thì bỏ gói)
  2. Cửa 0 trên thư mục gói (giấy phép, riêng tư, preview.html chạy ở 360/768/1280)
  3. ảnh: bìa tranh Public Domain + ghép hình, 4 ảnh chụp trang xem trước/bảng sprite/demo, GIF 10 s quay từ demo.html
  4. nén <chu-de>.zip, hồ sơ → đẩy net24-he-thong/BAN-GIAO/_cho-cua-1/ (GitHub chấm Cửa 1); mồi hàng đã lên kệ
"""
import argparse
import base64
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "KHUNG"))
sys.path.insert(0, str(HERE / "tools" / "chung"))
import goi  # noqa: E402
import moi  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Desktop\net24-he-thong"))
ORDER = ["platformer", "puzzle", "ui", "space", "tiles", "icons"]
ART = {"platformer": "forest", "puzzle": "still life", "ui": "interior", "space": "night sky", "tiles": "village", "icons": "objects"}


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with open(HERE / "NHAT-KY-chay.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def images(theme, info, out, stage):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    art_uri, credit = None, None
    try:
        import bia_sach
        img, credit, oid = bia_sach.find_art([ART[theme], "landscape"])
        if img is not None:
            img = bia_sach.cover_fill(img, 1600, 1200)
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=85)
            art_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
            credit = {"credit": credit, "object": oid}
    except Exception as e:
        log(f"tranh bia loi: {type(e).__name__}")
    pngs = sorted((stage / "PNG").glob("*.png"))
    pick = [p for i, p in enumerate(pngs) if i % max(1, len(pngs) // 24) == 0][:24]
    tiles = "".join(f"<div class='t'><img src='{p.resolve().as_uri()}'></div>" for p in pick)
    bg = f"url({art_uri}) center/cover" if art_uri else "linear-gradient(135deg,#14213D,#2D7FF9)"
    cover = (f"<html><head><meta charset='utf-8'><style>body{{margin:0;width:1600px;height:1200px;overflow:hidden;font-family:Inter,Segoe UI,Arial}}"
             ".t{background:#fff;border-radius:14px;display:flex;align-items:center;justify-content:center;height:120px}.t img{max-width:90px;max-height:90px;image-rendering:pixelated}"
             "</style></head><body><div style='position:absolute;inset:0;background:" + bg + "'></div>"
             "<div style='position:absolute;left:0;top:0;bottom:0;width:620px;background:rgba(10,20,45,.86);color:#fff;padding:120px 60px;box-sizing:border-box'>"
             "<div style='font:600 13px ui-monospace,Consolas;letter-spacing:.14em;color:#8FB8FF'>SNOUTSMITH STUDIO · CC0 GAME ASSETS</div>"
             f"<h1 style='font:400 64px/1.02 Georgia,serif;margin:20px 0'>{info['title']}</h1><div style='font-size:22px;color:#D6E4FF'>{info['sprites']} sprites · spritesheet + JSON atlas · playable demo</div>"
             "<div style='margin-top:34px;display:inline-block;background:#2D7FF9;border-radius:999px;padding:16px 30px;font-weight:700'>Free · CC0</div></div>"
             f"<div style='position:absolute;left:680px;top:140px;width:860px;display:grid;grid-template-columns:repeat(6,1fr);gap:14px;background:rgba(255,255,255,.18);padding:22px;border-radius:24px'>{tiles}</div></body></html>")
    out.mkdir(parents=True, exist_ok=True)
    (stage / "_cover.html").write_text(cover, encoding="utf-8")
    vid = out / "_vid"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 1600, "height": 1200})
        p.goto((stage / "_cover.html").resolve().as_uri())
        p.wait_for_timeout(600)
        p.screenshot(path=str(out / "cover-1600x1200.png"))
        p.goto((stage / "preview.html").resolve().as_uri())
        p.wait_for_timeout(800)
        p.screenshot(path=str(out / "anh-2-xem-truoc.png"))
        p.fill("#q", info["packs"][0]["pack"].replace("-", "")[:6])
        p.wait_for_timeout(400)
        p.screenshot(path=str(out / "anh-3-tim-kiem.png"))
        sheet = (stage / "spritesheet.png").resolve().as_uri()
        p.set_content(f"<body style='margin:0;background:repeating-conic-gradient(#e9eef8 0 25%,#fff 0 50%) 0 0/24px 24px;display:flex;align-items:center;justify-content:center;height:1200px'><img src='{sheet}' style='max-width:1500px;max-height:1100px;image-rendering:pixelated'></body>")
        p.wait_for_timeout(500)
        p.screenshot(path=str(out / "anh-4-spritesheet.png"))
        p.close()
        ctx = b.new_context(viewport={"width": 800, "height": 600}, record_video_dir=str(vid), record_video_size={"width": 800, "height": 600})
        d = ctx.new_page()
        d.goto((stage / "demo.html").resolve().as_uri())
        d.wait_for_timeout(11000)
        d.screenshot(path=str(out / "anh-5-demo.png"))
        video = d.video.path()
        ctx.close()
        b.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-t", "10", "-i", str(video), "-vf",
                    "fps=12,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse", str(out / "demo-10s.gif")], check=False)
    shutil.rmtree(vid, ignore_errors=True)
    (stage / "_cover.html").unlink()
    Image.open(out / "anh-2-xem-truoc.png").save(stage / "preview-1600x1200.png")
    if credit:
        (out / "COVER-CREDIT.json").write_text(json.dumps(credit, ensure_ascii=False), encoding="utf-8")
    return credit


def docs(theme, info, out, credit, c0):
    title = info["title"]
    t60 = f"{title} – {info['sprites']} CC0 Sprites"
    (out / "meta.json").write_text(json.dumps({"free": True, "xuong": "studio", "price": 0, "license": "CC0 – Kenney packs: " + ", ".join(p["pack"] for p in info["packs"]),
                                               "sprites": info["sprites"], "web": None}, indent=2), encoding="utf-8")
    (out / "LEADER.md").write_text(f"# LEADER – {title}\n\nLeader: gói CC0 của Kenney (kenney.nl – nguồn asset miễn phí được tải nhiều nhất cho game indie) và các gói CC0 nổi bật trên OpenGameArt.\n\n"
                                   "| # | Đặc điểm gói leader | Gói mình |\n|---|---|---|\n| 1 | PNG từng hình | ✅ PNG/ |\n| 2 | Spritesheet | ✅ spritesheet.png |\n"
                                   "| 3 | Tệp tọa độ (XML) | ✅ JSON atlas dạng TexturePacker (Phaser/PixiJS đọc thẳng) |\n| 4 | Ảnh xem trước | ✅ 5 ảnh + GIF |\n"
                                   "| 5 | Giấy phép CC0 rõ | ✅ LICENSE.txt + CREDITS.md |\n| 6 | Tên tệp có quy luật | ✅ <chu-de>_<goi>_<so>_<ten>.png |\n"
                                   "| 7 | Trang xem toàn bộ | ✅ preview.html có ô tìm |\n| 8 | Demo | ✅ demo.html chạy được |\n\n"
                                   "Giá trị thêm so với tải lẻ: gom 3 gói cùng chủ đề vào 1 bộ, 1 atlas chung, đặt tên thống nhất, trang tìm kiếm, demo.\n", encoding="utf-8")
    (out / "LICENSES.md").write_text("# LICENSES\n\n| Asset | Source | License |\n|---|---|---|\n"
                                     + "".join(f"| {p['sprites']} sprites | Kenney – {p['pack']} ({p['page']}) | CC0 1.0 (license.txt in the original pack) |\n" for p in info["packs"])
                                     + "| Atlas, naming, preview.html, demo.html, README | Snoutsmith Studio (`xuong/studio/KHUNG/goi.py`) | CC0 1.0 |\n"
                                     + (f"| Cover painting | {credit.get('credit', '')} | Public Domain / CC0 (museum open-access API flags it public domain) |\n" if credit else ""), encoding="utf-8")
    (out / "STORE.md").write_text("\n".join([
        f"# {t60}", "", f"Title ({len(t60)} chars): **{t60}**", "",
        f"{info['sprites']} hand-picked CC0 sprites from three Kenney packs, renamed into one scheme and packed into a single spritesheet with a JSON atlas. Drop it into Phaser or PixiJS and start building.", "",
        "- One spritesheet + TexturePacker-style JSON atlas (Phaser 3, PixiJS ready)", f"- {info['sprites']} individual PNGs with consistent file names",
        "- preview.html: browse and search every sprite", "- demo.html: a playable drop-and-bounce demo using the atlas", "- CC0: use in commercial games, no credit required", "",
        "## What you get", "", f"- `{theme}.zip` – PNG/, spritesheet.png, spritesheet.json, preview.html, demo.html, README.md, LICENSE.txt, CREDITS.md", "",
        "## FAQ", "", "**Can I use these in a paid game?** Yes, CC0 allows any use.", "",
        "**Do I have to credit anyone?** No, but crediting Kenney is kind; CREDITS.md lists the packs.", "",
        "**Which engines?** Any; the atlas format loads directly in Phaser 3 and PixiJS.", "",
        "**Are these the same as Kenney's free packs?** Yes, the sprites are Kenney's CC0 art; this bundle adds the merged atlas, naming, preview and demo.", "",
        "**What size are the sprites?** Mixed, up to 256 px; pixel-art packs are 16–18 px.", "",
        "## Price", "", "0 USD (KHUON-NHA-MAY mục 8: CC0 packs grouped by theme are free items).", "",
        "## Label", "", "Bundle assembled by code (AI-assisted tooling); all art is by Kenney, CC0.", "", "## Tags", "", f"{theme}, game assets, sprites, cc0, phaser, pixijs"]) + "\n", encoding="utf-8")
    (out / "BAN-GIAO.md").write_text(f"# Bàn giao: {t60}\n\n- Xưởng: Studio → studio.snoutsmith.com · giá 0 USD · {datetime.date.today():%d/%m/%Y}\n"
                                     f"- Tệp: `{theme}.zip` ({info['sprites']} hình, spritesheet {info['sheet'][0]}×{info['sheet'][1]}), bìa + 4 ảnh + GIF 10 s quay từ demo\n"
                                     f"- Cửa 0 trên thư mục gói: {c0}\n- Nguồn: " + ", ".join(p["page"] for p in info["packs"]) + "\n", encoding="utf-8")


def make(theme):
    out = HERE / "HANG" / f"{datetime.date.today():%Y%m%d}-{theme}"
    shutil.rmtree(out, ignore_errors=True)
    stage = out / "_goi"
    info = goi.build(theme, out)
    credit = images(theme, info, out, stage)
    docs(theme, info, out, credit, "")
    for name in ("BAN-GIAO.md", "LEADER.md", "LICENSES.md", "STORE.md", "meta.json"):
        shutil.copy2(out / name, stage / name)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(stage), "--web", "preview.html", "--free"], capture_output=True, text=True, encoding="utf-8", env=env)
    c0 = r.stdout.strip()[:160]
    for name in ("BAN-GIAO.md", "LEADER.md", "LICENSES.md", "STORE.md", "meta.json", "CUA0.json"):
        if (stage / name).exists():
            shutil.move(str(stage / name), str(out / name))
    shutil.rmtree(stage / "cua0-anh", ignore_errors=True)
    with zipfile.ZipFile(out / f"{theme}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(stage.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(stage))
    shutil.rmtree(stage)
    docs(theme, info, out, credit, c0)
    log(f"{theme}: {info['sprites']} hinh, zip {(out / f'{theme}.zip').stat().st_size // 1024} KB, {c0}")
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
        dest = NET24 / "BAN-GIAO" / "_cho-cua-1" / f"{date}-studio-{name}"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(item, dest)
        (item / ".da-day").write_text(f"{datetime.date.today()}", encoding="utf-8")
        sent.append(dest.name)
    if sent:
        subprocess.run(g + ["add", "BAN-GIAO/_cho-cua-1"])
        subprocess.run(g + ["commit", "-qm", f"Xuong Studio (may nha): {len(sent)} goi cho Cua 1"])
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
    q = [t for t in ORDER if t not in have]
    ra = qua = 0
    for t in q[:x.so_mon]:
        try:
            ok = make(t)
        except Exception as e:
            log(f"LOI {t}: {type(e).__name__}: {e}")
            continue
        ra += 1
        qua += bool(ok)
    n = 0
    if not x.khong_nop:
        n = day_cho_cua_1()
        log("moi hang len ke: " + json.dumps(moi.moi_len_ke("studio", NET24)))
    nk = HERE / "NHAT-KY.md"
    nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + f"\n| {datetime.date.today():%d/%m} | {ra} gói | Cửa 0: {qua} | đẩy chờ Cửa 1: {n} | 0 | {ra - qua} |\n", encoding="utf-8")
    log(f"XONG: ra {ra}, cua 0 {qua}, day {n}")


if __name__ == "__main__":
    main()
