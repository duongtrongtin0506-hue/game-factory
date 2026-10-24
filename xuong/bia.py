"""Bìa sản phẩm từ ẢNH CHỤP THẬT (không tranh không liên quan): nền 1 màu, tiêu đề ≤ 6 chữ, 1–2 ảnh chụp có bo góc + bóng.
  python xuong/bia.py <out.png> "<Tiêu đề>" "<Phụ đề>" <#màu-nhấn> <ảnh1.png> [ảnh2.png] [--size 1600x1200]
Một font (Segoe UI / DejaVu Sans), 1 màu nhấn – theo NHIEM-VU/CHUAN-THIET-KE.md.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = {"b": ["C:/Windows/Fonts/seguisb.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
         "r": ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]}


def font(kind, size):
    for f in FONTS[kind]:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def card(img, maxw, maxh, r=28):
    img = img.convert("RGB")
    img.thumbnail((maxw, maxh), Image.LANCZOS)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, *img.size], r, fill=255)
    return img, m


def bia(out, title, sub, accent, shots, size=(1600, 1200)):
    W, H = size
    bg = Image.new("RGB", size, "#F5F5F7")
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, W, 14], fill=accent)
    tf, sf = font("b", int(W * .052)), font("r", int(W * .022))
    d.text((W * .07, H * .09), title, font=tf, fill="#1D1D1F")
    d.text((W * .07, H * .09 + tf.size * 1.35), sub, font=sf, fill="#6E6E73")
    top = int(H * .09 + tf.size * 1.35 + sf.size * 2.4)
    imgs = [Image.open(s) for s in shots[:2]]
    n = len(imgs)
    slot_w, slot_h = int(W * (.84 if n == 1 else .41)), H - top - int(H * .06)
    x = int(W * .08)
    for im in imgs:
        c, m = card(im, slot_w, slot_h)
        sh = Image.new("RGBA", (c.width + 80, c.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([40, 50, 40 + c.width, 50 + c.height], 28, fill=(0, 0, 0, 60))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        cx = x + (slot_w - c.width) // 2
        bg.paste(sh, (cx - 40, top - 40), sh)
        bg.paste(c, (cx, top), m)
        x += slot_w + int(W * .02)
    bg.save(out, optimize=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    size = (1600, 1200)
    if "--size" in a:
        i = a.index("--size"); size = tuple(int(v) for v in a[i + 1].split("x")); del a[i:i + 2]
    bia(a[0], a[1], a[2], a[3], a[4:], size)
