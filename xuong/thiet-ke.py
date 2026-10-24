"""Cửa 0 vòng 3+4: đo và ghi THIET-KE.md cho 1 thư mục hàng (NHIEM-VU/CHUAN-THIET-KE.md mục 4) + quét chữ nội bộ.
  python xuong/thiet-ke.py <thư-mục-hàng> [--mau "#chữ:#nền" ...] [--chu 16] [--font "System UI"] [--them "dòng đo thêm"]...
Thoát mã 1 nếu: lộ chữ nội bộ ở hồ sơ khách thấy, < 5 ảnh, thiếu GIF/video, tương phản < 4.5, chữ thân < 16px.
"""
import json, re, sys, zipfile
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


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    d = Path(a[0]); opt = {"mau": [], "them": []}; i = 1
    while i < len(a):
        k = a[i].lstrip("-"); opt.setdefault(k, []).append(a[i + 1]) if k in ("mau", "them") else opt.__setitem__(k, a[i + 1]); i += 2
    loi, dong = [], []
    imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not p.name.startswith("icon"))
    gifs = [p for p in d.iterdir() if p.suffix.lower() in (".gif", ".mp4", ".webm")]
    for p in imgs:
        with Image.open(p) as im:
            dong.append(f"| Ảnh | {p.name} | {im.width}×{im.height} px · {p.stat().st_size // 1024} KB |")
    for p in gifs:
        dong.append(f"| Động | {p.name} | {p.stat().st_size // 1024} KB |")
    if len(imgs) < 5: loi.append(f"chỉ {len(imgs)} ảnh < 5")
    if not gifs: loi.append("thiếu GIF/video")
    for m in opt["mau"]:
        fg, bg = m.split(":"); r = ratio(fg, bg)
        dong.append(f"| Tương phản | {fg} trên {bg} | {r:.1f}:1 {'✅' if r >= 4.5 else '❌'} (≥ 4.5) |")
        if r < 4.5: loi.append(f"tương phản {fg}/{bg} {r:.1f}")
    chu = int(opt.get("chu", 16))
    dong.append(f"| Chữ thân | {opt.get('font', 'system-ui')} | {chu}px {'✅' if chu >= 16 else '❌'} (≥ 16) |")
    if chu < 16: loi.append("chữ thân < 16px")
    for z in d.glob("*.zip"):
        dong.append(f"| Gói tải | {z.name} | {z.stat().st_size / 1024:.0f} KB {'✅' if z.stat().st_size < 2 * 2**20 else '❌'} (< 2 MB) · {len(zipfile.ZipFile(z).namelist())} tệp |")
    for f in d.glob("*.epub"):
        dong.append(f"| Gói tải | {f.name} | {f.stat().st_size / 1024:.0f} KB |")
    for f in d.glob("*.pdf"):
        dong.append(f"| Gói tải | {f.name} | {f.stat().st_size / 1024:.0f} KB |")
    for f in d.glob("*.xlsx"):
        dong.append(f"| Gói tải | {f.name} | {f.stat().st_size / 1024:.0f} KB |")
    lo = sorted({m.group(0) for f in KHACH if (d / f).exists() for m in NOI_BO.finditer((d / f).read_text(encoding="utf-8", errors="ignore"))})
    dong.append(f"| Chữ nội bộ | {', '.join(KHACH)} | {'0 ✅' if not lo else '❌ ' + ', '.join(lo)} |")
    if lo: loi.append("lộ chữ nội bộ: " + ", ".join(lo))
    for t in opt["them"]:
        dong.append("| " + t + " |")
    md = ["# Design measurements (pre-submission check)", "", "| Check | Item | Measured |", "|---|---|---|", *dong, "",
          f"Result: {'PASS' if not loi else 'FAIL – ' + '; '.join(loi)}", ""]
    (d / "THIET-KE.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
