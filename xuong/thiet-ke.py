"""Cửa 0 vòng 3+4: đo và ghi THIET-KE.md cho 1 thư mục hàng (NHIEM-VU/CHUAN-THIET-KE.md mục 4) + quét chữ nội bộ.
  python xuong/thiet-ke.py <thư-mục-hàng> [--mau "#chữ:#nền" ...] [--chu 16] [--font "System UI"] [--them "Check | Item | Measured"]...
Thoát mã 1 nếu: lộ chữ nội bộ ở hồ sơ khách thấy, < 5 ảnh, thiếu GIF/video, tương phản < 4.5, chữ thân < 16px.
Đạt → chép bảng số đo vào BAN-GIAO.md (Cửa 1 chỉ đọc BAN-GIAO/LEADER/STORE/LICENSES – bài học 24/10: thiết kế 70 vì không thấy số đo).
"""
import re, sys, zipfile
from pathlib import Path
from PIL import Image

NOI_BO = re.compile(r"(?i)\b(claude|anthropic|khuon[- ]nha[- ]may|KHUON-NHA-MAY|cua[- ]?[01]\b|n24[-_][a-z]+|AI built by code|copied from leaders|BAN-GIAO|YEU-CAU|HOP-LENH)")
KHACH = ("STORE.md", "BAN-GIAO.md", "LEADER.md", "LICENSES.md")


def lum(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + .05) / (lb + .05)


def gif_info(p):
    fr = ms = 0
    try:
        with Image.open(p) as g:
            while True:
                fr += 1; ms += g.info.get("duration", 0); g.seek(g.tell() + 1)
    except Exception:
        pass
    return fr, ms


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    d = Path(a[0]); opt = {"mau": [], "them": []}; i = 1
    while i < len(a):
        k = a[i].lstrip("-")
        if k in ("mau", "them"): opt[k].append(a[i + 1])
        else: opt[k] = a[i + 1]
        i += 2
    loi, dong = [], []
    imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not p.name.startswith("icon"))
    gifs = sorted(p for p in d.iterdir() if p.suffix.lower() in (".gif", ".mp4", ".webm"))
    for p in imgs:
        with Image.open(p) as im:
            dong.append(f"| Image | {p.name} | {im.width}×{im.height} px · {p.stat().st_size // 1024} KB |")
    for p in gifs:
        fr, ms = gif_info(p) if p.suffix.lower() == ".gif" else (0, 0)
        dong.append(f"| Motion | {p.name} | {p.stat().st_size // 1024} KB" + (f" · {fr} frames · {ms / 1000:.1f} s loop |" if fr else " |"))
    if len(imgs) < 5: loi.append(f"only {len(imgs)} images (< 5)")
    if not gifs: loi.append("no GIF/video")
    for m in opt["mau"]:
        fg, bg = m.split(":"); r = ratio(fg, bg)
        dong.append(f"| Contrast | {fg} on {bg} | {r:.1f}:1 {'✅' if r >= 4.5 else '❌'} (WCAG AA ≥ 4.5) |")
        if r < 4.5: loi.append(f"contrast {fg}/{bg} {r:.1f}")
    chu = int(opt.get("chu", 16))
    dong.append(f"| Body text | {opt.get('font', 'system-ui')} | {chu}px {'✅' if chu >= 16 else '❌'} (≥ 16) |")
    if chu < 16: loi.append("body text < 16px")
    for z in d.glob("*.zip"):
        n = zipfile.ZipFile(z)
        js = sum(x.file_size for x in n.infolist() if x.filename.endswith(".js"))
        dong.append(f"| Download | {z.name} | {z.stat().st_size / 1024:.0f} KB {'✅' if z.stat().st_size < 2 * 2**20 else '❌'} (< 2 MB) · {len(n.namelist())} files · JS {js / 1024:.1f} KB |")
    for ext in ("*.epub", "*.pdf", "*.xlsx"):
        for f in d.glob(ext):
            dong.append(f"| Download | {f.name} | {f.stat().st_size / 1024:.0f} KB |")
    lo = sorted({m.group(0) for f in KHACH if (d / f).exists() for m in NOI_BO.finditer((d / f).read_text(encoding="utf-8", errors="ignore"))})
    dong.append(f"| Internal words | {', '.join(KHACH)} | {'0 ✅' if not lo else '❌ ' + ', '.join(lo)} |")
    if lo: loi.append("internal words: " + ", ".join(lo))
    for t in opt["them"]:
        dong.append("| " + t + " |")
    tbl = ["| Check | Item | Measured |", "|---|---|---|", *dong]
    md = ["# Design measurements (pre-submission check)", "", *tbl, "", f"Result: {'PASS' if not loi else 'FAIL – ' + '; '.join(loi)}", ""]
    (d / "THIET-KE.md").write_text("\n".join(md), encoding="utf-8")
    bg = d / "BAN-GIAO.md"
    if bg.exists() and not loi:
        t = bg.read_text(encoding="utf-8").split("\n## Design measurements")[0].rstrip("\n")
        bg.write_text(t + "\n\n## Design measurements (measured before submission)\n\n" + "\n".join(tbl) + "\n", encoding="utf-8")
    print("\n".join(md))
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
