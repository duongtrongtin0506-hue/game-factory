"""Xưởng Media cho sàn nội địa (Agent 5: Shopee / TikTok Shop) – chạy đêm trên máy nhà: python chay.py [--so-mon 20]

1. Quét kho video review (thư mục trong biến MEDIA_DIRS, cách nhau bằng ';'; mặc định các thư mục trong MEDIA-DIRS.txt)
   → KHO-VIDEO.csv (tệp · thời lượng · chủ đề đoán theo tên · cỡ MB). Không quét thư mục kênh YouTube/game.
2. Đọc net24-he-thong/12-Da-kenh/THIEU-MEDIA.csv (san,sku,id,ten,so_anh,co_video – máy Agent 5 xuất mỗi ngày).
3. Mỗi sản phẩm thiếu media: khớp video theo tên (từ chung nhiều nhất); không có thì dựng video 9:16 (10 giây, chữ tiếng Việt,
   không nhạc) từ ảnh sản phẩm ở 12-Da-kenh/anh/<sku>/ bằng ffmpeg; kèm 5 ảnh 1:1 nền sạch (1080×1080).
4. Giao BAN-GIAO/_noi-dia/<sku>/ (video.mp4 ≤ 30 MB, anh-1..5.jpg, meta.json {ma_sp, nguon}) → commit + push; nhịp tim.
Thiếu ảnh và thiếu video khớp → ghi vào NHAT-KY-chay.txt, không giao món rỗng.
"""
import argparse
import csv
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sach" / "tools" / "chung"))
import nhip  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))
SKIP = re.compile(r"kenh-video|noi-dung-video|GAME[\\/]web|BAN-GIAO", re.I)
FONT = r"C\:/Windows/Fonts/arial.ttf"


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with open(HERE / "NHAT-KY-chay.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def words(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")
    return {w for w in re.findall(r"[a-z0-9]{3,}", s)}


def dirs():
    env = os.environ.get("MEDIA_DIRS", "")
    lst = [d for d in env.split(";") if d.strip()]
    f = HERE / "MEDIA-DIRS.txt"
    if f.exists():
        lst += [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    return [Path(d) for d in lst if Path(d).exists()]


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 1)
    except Exception:
        return 0.0


def quet():
    rows = []
    for d in dirs():
        for p in d.rglob("*"):
            if p.suffix.lower() in (".mp4", ".mov", ".webm") and not SKIP.search(str(p)):
                rows.append({"tep": str(p), "giay": duration(p), "chu_de": " ".join(sorted(words(p.stem)))[:80], "mb": round(p.stat().st_size / 1e6, 1)})
    with open(HERE / "KHO-VIDEO.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tep", "giay", "chu_de", "mb"])
        w.writeheader()
        w.writerows(rows)
    return rows


def khop(ten, kho):
    tw = words(ten)
    best, score = None, 0
    for v in kho:
        s = len(tw & set(v["chu_de"].split()))
        if s > score and v["mb"] <= 30:
            best, score = v, s
    return best if score >= 2 else None


def anh_vuong(src_imgs, out):
    from PIL import Image, ImageOps
    made = []
    for i, p in enumerate(src_imgs[:5], 1):
        im = Image.open(p).convert("RGB")
        im = ImageOps.contain(im, (980, 980))
        bg = Image.new("RGB", (1080, 1080), (250, 250, 250))
        bg.paste(im, ((1080 - im.width) // 2, (1080 - im.height) // 2))
        bg.save(out / f"anh-{i}.jpg", quality=90)
        made.append(out / f"anh-{i}.jpg")
    return made


def video_tu_anh(imgs, ten, out):
    """9:16, ~10 s, slow zoom per image, Vietnamese caption, no music."""
    lst = out / "_list.txt"
    per = max(2.0, 10.0 / len(imgs))
    lst.write_text("".join(f"file '{p.as_posix()}'\nduration {per}\n" for p in imgs) + f"file '{imgs[-1].as_posix()}'\n", encoding="utf-8")
    cap = out / "_cap.txt"
    cap.write_text(ten[:60], encoding="utf-8")
    vf = (f"scale=1080:1080,pad=1080:1920:0:420:white,drawtext=fontfile='{FONT}':textfile='{cap.as_posix()}':fontsize=54:fontcolor=black:x=(w-text_w)/2:y=180,"
          f"drawtext=fontfile='{FONT}':text='Xem chi tiết trong giỏ hàng':fontsize=40:fontcolor=0xE8833A:x=(w-text_w)/2:y=1620,fps=30,format=yuv420p")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", vf, "-t", "10", "-c:v", "libx264", "-crf", "24", str(out / "video.mp4")])
    lst.unlink(missing_ok=True)
    cap.unlink(missing_ok=True)
    return r.returncode == 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("--so-mon", type=int, default=20)
    a.add_argument("--khong-nop", action="store_true")
    x = a.parse_args()
    subprocess.run(["git", "-C", str(NET24), "pull", "-q", "--rebase", "--autostash"])
    kho = quet()
    log(f"kho video: {len(kho)} tệp từ {len(dirs())} thư mục")
    src = NET24 / "12-Da-kenh" / "THIEU-MEDIA.csv"
    rows = list(csv.DictReader(open(src, encoding="utf-8"))) if src.exists() else []
    done = 0
    for r in rows:
        if done >= x.so_mon:
            break
        sku = (r.get("sku") or r.get("id") or "").strip()
        if not sku:
            continue
        out = NET24 / "BAN-GIAO" / "_noi-dia" / re.sub(r"[^A-Za-z0-9_-]+", "-", sku)
        if (out / "meta.json").exists():
            continue
        imgs = sorted(p for p in (NET24 / "12-Da-kenh" / "anh" / sku).glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) if (NET24 / "12-Da-kenh" / "anh" / sku).exists() else []
        v = khop(r.get("ten", ""), kho)
        if not imgs and not v:
            log(f"{sku}: không có ảnh nguồn và không có video khớp – bỏ qua")
            continue
        out.mkdir(parents=True, exist_ok=True)
        nguon = []
        if imgs:
            anh_vuong(imgs, out)
            nguon.append("anh san pham 12-Da-kenh/anh/" + sku)
        if v:
            shutil.copy2(v["tep"], out / "video.mp4")
            nguon.append("kho video: " + Path(v["tep"]).name)
        elif imgs and video_tu_anh(sorted(out.glob("anh-*.jpg")), r.get("ten", sku), out):
            nguon.append("video dung tu anh (ffmpeg)")
        (out / "meta.json").write_text(json.dumps({"ma_sp": sku, "san": r.get("san", ""), "ten": r.get("ten", ""), "nguon": nguon,
                                                   "ngay": str(datetime.date.today())}, ensure_ascii=False, indent=1), encoding="utf-8")
        done += 1
        log(f"{sku}: {', '.join(nguon)}")
    if done and not x.khong_nop:
        g = ["git", "-C", str(NET24)]
        subprocess.run(g + ["add", "BAN-GIAO/_noi-dia"])
        subprocess.run(g + ["commit", "-qm", f"Xuong Media (may nha): {done} san pham noi dia"])
        subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
        subprocess.run(g + ["push", "-q"])
    log(f"XONG: thiếu media {len(rows)} sản phẩm, giao {done}")
    if not x.khong_nop:
        nhip.nhip("media", done, NET24)


if __name__ == "__main__":
    main()
