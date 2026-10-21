#!/usr/bin/env python3
"""Dựng bìa sách cổ điển kiểu Standard Ebooks / Penguin Classics (21/10/2026).

Tranh nền: tác phẩm PUBLIC DOMAIN (CC0) của The Met Open Access, tự tìm theo từ khóa từng cuốn.
Bố cục: tranh phủ kín → dải màu thương hiệu phía dưới → tên sách (Cormorant) + tác giả + nhãn nhà sách + ghi công tranh.
Dùng: python scripts/bia-sach.py danh-sach.json thu-muc-ra/
danh-sach.json: [{"slug","title","author","q":["từ khóa 1","từ khóa 2"]}]
"""
import io, json, os, sys, textwrap, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1600, 2560
GREEN = (30, 70, 54)
CREAM = (244, 237, 224)
GOLD = (216, 178, 110)
UA = {"User-Agent": "SnoutsmithBooks-cover/1.0 (books.snoutsmith.com)"}
FONTS = {
    "serif": "https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
    "serif_i": "https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf",
    "sans": "https://raw.githubusercontent.com/google/fonts/main/ofl/jost/Jost%5Bwght%5D.ttf",
}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={**UA, "AIC-User-Agent": UA["User-Agent"]})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
    except Exception as e:
        raise RuntimeError(f"{e} @ {url[:90]}")
    return data if binary else json.loads(data)


def font(kind, size):
    import tempfile
    path = os.path.join(tempfile.gettempdir(), f"{kind}.ttf")
    if not os.path.exists(path):
        try:
            open(path, "wb").write(get(FONTS[kind], True))
        except Exception as e:
            print("font", kind, e)
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        alt = {"serif": "DejaVuSerif-Bold.ttf", "serif_i": "DejaVuSerif-Italic.ttf", "sans": "DejaVuSans.ttf"}[kind]
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + alt, size)
    try:
        f.set_variation_by_axes([600 if kind != "sans" else 500])
    except Exception:
        pass
    return f


USED = set()  # không dùng trùng 1 tranh trong cùng 1 lô


def find_art_aic(queries):
    """Art Institute of Chicago – ảnh Public Domain (CC0), API ổn định."""
    for q in queries:
        url = ("https://api.artic.edu/api/v1/artworks/search?q=" + urllib.parse.quote(q)
               + "&query%5Bterm%5D%5Bis_public_domain%5D=true&limit=25&fields=id,title,image_id,artist_title,date_display,classification_title")
        try:
            data = get(url).get("data") or []
        except Exception as e:
            print("aic", e)
            continue
        for o in data:
            if not o.get("image_id") or o["id"] in USED:
                continue
            if "painting" not in (o.get("classification_title") or "").lower():
                continue
            try:
                img = Image.open(io.BytesIO(get(f"https://www.artic.edu/iiif/2/{o['image_id']}/full/1686,/0/default.jpg", True))).convert("RGB")
            except Exception as e:
                print("aic img", e)
                continue
            if min(img.size) < 800:
                continue
            credit = f'{(o.get("title") or "")[:60]} – {o.get("artist_title") or "Unknown artist"}, {o.get("date_display") or ""}. Art Institute of Chicago, Public Domain (CC0)'
            USED.add(o["id"])
            return img, credit, "aic-" + str(o["id"])
    return None, None, None


def find_art(queries):
    img, credit, oid = find_art_aic(queries)
    if img is not None:
        return img, credit, oid
    for q in queries:
        try:
            s = get("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isPublicDomain=true&q=" + urllib.parse.quote(q))
        except Exception as e:
            print("met", e)
            continue
        for oid in (s.get("objectIDs") or [])[:40]:
            try:
                o = get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
            except Exception:
                continue
            if not o.get("isPublicDomain") or not o.get("primaryImage"):
                continue
            if o.get("classification") not in ("Paintings", "Drawings", "Prints"):
                continue
            try:
                img = Image.open(io.BytesIO(get(o["primaryImage"], True))).convert("RGB")
            except Exception:
                continue
            if min(img.size) < 900:
                continue
            credit = f'{o.get("title","")[:60]} – {o.get("artistDisplayName") or "Unknown artist"}, {o.get("objectDate","")}. The Met, Public Domain (CC0)'
            return img, credit, oid
    return None, None, None


def cover_fill(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, max(0, int((img.height - h) * 0.35))
    return img.crop((x, y, x + w, y + h))


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    # cân dòng: dòng cuối quá ngắn (1 chữ) thì kéo bớt chữ từ dòng trên xuống
    if len(lines) >= 2 and len(lines[-1].split()) == 1:
        prev = lines[-2].split()
        if len(prev) >= 3:
            lines[-2] = " ".join(prev[:-1])
            lines[-1] = prev[-1] + " " + lines[-1]
    return lines


def make(b, outdir):
    art, credit, oid = find_art(b["q"])
    band_top = int(H * 0.60)
    if art is None:
        base = Image.new("RGB", (W, H), GREEN)
        credit = "Cover design: Snoutsmith Books"
    else:
        base = cover_fill(art, W, band_top + 40)
        canvas = Image.new("RGB", (W, H), GREEN)
        canvas.paste(base, (0, 0))
        base = canvas
    d = ImageDraw.Draw(base)
    # dải trên mờ để nhãn đọc được
    top = base.crop((0, 0, W, 220)).filter(ImageFilter.GaussianBlur(2))
    shade = Image.new("RGB", (W, 220), (0, 0, 0))
    base.paste(Image.blend(top, shade, 0.45), (0, 0))
    d = ImageDraw.Draw(base)
    lab = font("sans", 34)
    t = "SNOUTSMITH BOOKS  ·  MONEY CLASSICS"
    d.text(((W - d.textlength(t, font=lab)) / 2, 92), t, font=lab, fill=CREAM, spacing=4)
    # dải màu tên sách
    d.rectangle((0, band_top, W, H), fill=GREEN)
    d.rectangle((0, band_top, W, band_top + 10), fill=GOLD)
    tf = font("serif", 150)
    lines = wrap(d, b["title"], tf, W - 240)
    if len(lines) > 3:
        tf = font("serif", 118)
        lines = wrap(d, b["title"], tf, W - 220)
    y = band_top + 150
    for ln in lines:
        d.text(((W - d.textlength(ln, font=tf)) / 2, y), ln, font=tf, fill=CREAM)
        y += int(tf.size * 1.08)
    d.line(((W / 2 - 90), y + 40, (W / 2 + 90), y + 40), fill=GOLD, width=4)
    af = font("serif_i", 78)
    d.text(((W - d.textlength(b["author"], font=af)) / 2, y + 80), b["author"], font=af, fill=GOLD)
    ed = font("sans", 30)
    t = "THE CLEAN EDITION"
    d.text(((W - d.textlength(t, font=ed)) / 2, H - 190), t, font=ed, fill=CREAM)
    cf = font("sans", 20)
    for i, ln in enumerate(textwrap.wrap(credit, 120)[:2]):
        d.text(((W - d.textlength(ln, font=cf)) / 2, H - 110 + i * 28), ln, font=cf, fill=(170, 190, 178))
    os.makedirs(f"{outdir}/{b['slug']}", exist_ok=True)
    base.save(f"{outdir}/{b['slug']}/cover-1600x2560.png", optimize=True)
    base.resize((160, 256), Image.LANCZOS).save(f"{outdir}/{b['slug']}/cover-160x256.png")
    json.dump({"met_object": oid, "credit": credit}, open(f"{outdir}/{b['slug']}/COVER-CREDIT.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("ok", b["slug"], oid)


if __name__ == "__main__":
    books = json.load(open(sys.argv[1]))
    for b in books:
        try:
            make(b, sys.argv[2])
        except Exception as e:  # một cuốn lỗi không dừng cả lô
            print("loi", b["slug"], e)
