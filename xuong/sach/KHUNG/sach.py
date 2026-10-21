"""Public-domain classic -> clean edition (EPUB 3 + 6x9 PDF + 1600x2560 cover), Snoutsmith Books · Money Classics.

python KHUNG/sach.py <gutenberg-id> [--out HANG/<date>-<slug>]   (one book)
Steps: download the Project Gutenberg HTML, remove every Project Gutenberg header, footer, license and
mention (their trademark may not stay in a redistributed edition), drop images and links, split into chapters,
write our own title page, "About this edition" and contents, build a valid EPUB 3, print a 6x9 in PDF with
page numbers (Chromium via Playwright, EB Garamond OFL), draw the cover with Pillow. Writes BAN-GIAO.md,
LICENSES.md, CREDITS.md, STORE.md, meta.json for Cửa 0/1.
"""
import argparse
import datetime
import html
import io
import json
import re
import subprocess
import sys
import textwrap
import uuid
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup, Comment
from lxml import etree
from lxml import html as lhtml

K = Path(__file__).resolve().parent
ROOT = K.parent
FONTS = K / "fonts"
UA = {"User-Agent": "Mozilla/5.0 (net24 xuong-sach; public-domain edition builder)"}
ACCENT = (178, 58, 72)   # #B23A48 books shop accent
SERIES = "Snoutsmith Books · Money Classics"


def fetch(url):
    import urllib.request
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            return r.read()
    except Exception:
        # Machines behind a TLS-inspecting proxy: curl uses the system certificate store.
        return subprocess.run(["curl", "-sfL", "-A", UA["User-Agent"], url], capture_output=True, check=True).stdout


BLOCKS = ["p", "div", "pre", "section", "table", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "span"]


def clean(raw):
    soup = BeautifulSoup(raw, "lxml")
    for t in soup(["script", "style", "img", "figure", "head", "meta", "link"]):
        t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.select("section.pg-boilerplate, #pg-header, #pg-footer, .pg-boilerplate, #pg-machine-header, #pg-start-separator, #pg-end-separator"):
        t.decompose()
    # Old-style files: everything before "*** START OF" and after "*** END OF" is Project Gutenberg's.
    body = soup.body or soup
    text_nodes = body.find_all(string=re.compile(r"\*\*\*\s*(START|END) OF (THE|THIS) PROJECT GUTENBERG", re.I))
    for node in text_nodes:
        blk = node.find_parent(BLOCKS) or node.parent
        start = "START" in node.upper()
        sib = blk.previous_sibling if start else blk.next_sibling
        while sib is not None:
            nxt = sib.previous_sibling if start else sib.next_sibling
            sib.extract()
            sib = nxt
        blk.decompose()
    # Any remaining mention: drop the smallest block holding it (never the whole book).
    for node in body.find_all(string=re.compile(r"gutenberg", re.I)):
        if node.parent is None:
            continue
        blk = node.find_parent(BLOCKS)
        if blk is not None and len(blk.get_text()) < 3000:
            blk.decompose()
        else:
            node.replace_with(re.sub(r"(?i)project gutenberg[^.]*\.?", "", str(node)))
    for a in body.find_all("a"):
        a.unwrap()
    for t in body.find_all(True):
        for attr in list(t.attrs):
            if attr not in ("id", "class", "colspan", "rowspan"):
                del t.attrs[attr]
        if t.get("class"):
            t["class"] = [c for c in t["class"] if c in ("center", "right", "smcap", "poem", "stanza", "verse")]
            if not t["class"]:
                del t["class"]
    return body


SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "the", "to", "with", "from"}


def nice_title(t):
    if not t.isupper():
        return t
    w = t.lower().split()
    return " ".join(x if (i and x in SMALL) else x[:1].upper() + x[1:] for i, x in enumerate(w))


def split_at(body, level):
    flat = []
    def flatten(node):
        for ch in list(node.children):
            if getattr(ch, "name", None) in ("div", "section") and ch.find(level):
                flatten(ch)
            else:
                flat.append(ch)
    flatten(body)
    out, cur_title, cur = [], "Opening", []
    for el in flat:
        if getattr(el, "name", None) == level:
            if cur and any(str(x).strip() for x in cur):
                out.append((cur_title, cur))
            cur_title, cur = " ".join(el.get_text(" ").split())[:120] or "Chapter", [el]
        else:
            cur.append(el)
    if cur:
        out.append((cur_title, cur))
    return [(t, "".join(str(e) for e in els if str(e).strip())) for t, els in out]


def chapters(body):
    """Pick the heading level that gives the most real chapters (>= 3 sections, average >= 350 words), split there,
    drop the original contents page and title-page fragments, return [(title, xhtml)]."""
    best = None
    for level in ("h1", "h2", "h3", "h4"):
        secs = split_at(body, level)
        n = [len(BeautifulSoup(f, "lxml").get_text(" ").split()) for _, f in secs]
        if len(secs) >= 3 and sum(n) / len(n) >= 350 and (best is None or len(secs) > len(best)):
            best = secs
    secs = best or split_at(body, "h2")
    result, started = [], False
    for title, frag in secs:
        n = len(BeautifulSoup(frag, "lxml").get_text(" ").split())
        if re.fullmatch(r"(table of )?contents\.?", title.strip(), re.I):
            continue
        if not started and n < 120:
            continue
        started = True
        result.append((nice_title(title), to_xhtml(frag)))
    return result

def to_xhtml(frag):
    wrapper = lhtml.fragment_fromstring(frag or "<p></p>", create_parent="div")
    s = etree.tostring(wrapper, method="xml", encoding="unicode")
    return s[len("<div>"):-len("</div>")] if s.startswith("<div>") else s


XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{title}</title><link rel="stylesheet" type="text/css" href="../style.css"/></head>
<body>{body}</body></html>"""
CSS = """body{font-family:"EB Garamond",Georgia,serif;line-height:1.5;margin:0 4%;}
h1,h2,h3{font-weight:400;line-height:1.2;margin:1.6em 0 .8em;text-align:center}
h2{font-size:1.5em}p{margin:0;text-indent:1.4em;text-align:justify;hyphens:auto}
h1+p,h2+p,h3+p,.noindent{text-indent:0}blockquote{margin:1em 2em;font-style:italic}
.center{text-align:center;text-indent:0}.series{font-family:Inter,sans-serif;font-size:.7em;letter-spacing:.12em;text-transform:uppercase;color:#B23A48;text-align:center}
.titlepage h1{font-size:2.2em;margin-top:30%}.author{text-align:center;font-style:italic;text-indent:0;margin-top:1em}
table{margin:1em auto;border-collapse:collapse}td{padding:.2em .5em}pre{white-space:pre-wrap;font-family:inherit}"""


def esc(s):
    return html.escape(s, quote=True)


def build_epub(meta, chs, cover_jpg, path):
    bid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "snoutsmith-books/" + meta["slug"]))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = {}
    title_page = (f'<section class="titlepage" epub:type="titlepage"><p class="series">{esc(SERIES)}</p><h1>{esc(meta["title"])}</h1>'
                  f'<p class="author">{esc(meta["author"])}</p>' + (f'<p class="center" style="margin-top:3em">First published {esc(str(meta["year"]))}</p>' if meta.get("year") else "") + '</section>')
    about = ("<section epub:type=\"preface\"><h2>About this edition</h2>" + "".join(f"<p>{esc(p)}</p>" for p in meta["about"]) + "</section>")
    files["text/title.xhtml"] = XHTML.format(title=esc(meta["title"]), body=title_page)
    files["text/about.xhtml"] = XHTML.format(title="About this edition", body=about)
    toc = []
    for i, (t, body) in enumerate(chs, 1):
        name = f"text/ch{i:03d}.xhtml"
        files[name] = XHTML.format(title=esc(t), body=f"<section>{body}</section>")
        toc.append((name, t))
    files["cover.xhtml"] = XHTML.replace("../style.css", "style.css").format(title="Cover", body='<div style="text-align:center"><img src="images/cover.jpg" alt="Cover" style="max-width:100%;max-height:100vh"/></div>')
    nav = ('<nav epub:type="toc" id="toc"><h2>Contents</h2><ol><li><a href="text/about.xhtml">About this edition</a></li>'
           + "".join(f'<li><a href="{n}">{esc(t)}</a></li>' for n, t in toc) + "</ol></nav>")
    files["nav.xhtml"] = XHTML.replace("../style.css", "style.css").format(title="Contents", body=nav)
    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="cover-img" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
                '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="title" href="text/title.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="about" href="text/about.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="cover"/>', '<itemref idref="title"/>', '<itemref idref="nav"/>', '<itemref idref="about"/>']
    for i, (n, _) in enumerate(toc, 1):
        manifest.append(f'<item id="c{i}" href="{n}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="c{i}"/>')
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{bid}</dc:identifier><dc:title>{esc(meta["title"])}</dc:title><dc:creator>{esc(meta["author"])}</dc:creator>
<dc:language>en</dc:language><dc:publisher>Snoutsmith Books</dc:publisher><dc:rights>Text in the public domain. Edition design and front matter © Snoutsmith Books.</dc:rights>
<meta property="dcterms:modified">{now}</meta><meta name="cover" content="cover-img"/>
</metadata>
<manifest>{''.join(manifest)}</manifest>
<spine>{''.join(spine)}</spine>
</package>"""
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>"""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/images/cover.jpg", cover_jpg, compress_type=zipfile.ZIP_DEFLATED)
        for name, text in files.items():
            z.writestr("OEBPS/" + name, text, compress_type=zipfile.ZIP_DEFLATED)
    return len(toc)


def cover(meta, path_png, size=(1600, 2560)):
    from PIL import Image, ImageDraw, ImageFont
    W, H = size
    im = Image.new("RGB", size, (250, 246, 239))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.06)], fill=ACCENT)
    d.rectangle([0, int(H * 0.94), W, H], fill=ACCENT)
    serif = lambda s: ImageFont.truetype(str(FONTS / "EBGaramond.ttf"), s)
    sans = lambda s: ImageFont.truetype(str(FONTS / "Inter.ttf"), s)
    lab = sans(40)
    d.text((W / 2, int(H * 0.12)), SERIES.upper(), font=lab, fill=ACCENT, anchor="mm")
    words = meta["title"].split()
    size_t = 210 if len(meta["title"]) < 22 else 170 if len(meta["title"]) < 34 else 140
    f = serif(size_t)
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > W * 0.82 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    y = int(H * 0.36) - len(lines) * size_t * 0.55
    for ln in lines:
        d.text((W / 2, y), ln, font=f, fill=(26, 26, 26), anchor="mm")
        y += size_t * 1.08
    d.line([(W * 0.42, y + 40), (W * 0.58, y + 40)], fill=ACCENT, width=6)
    d.text((W / 2, y + 150), meta["author"], font=ImageFont.truetype(str(FONTS / "EBGaramond-Italic.ttf"), 96), fill=(60, 52, 46), anchor="mm")
    if meta.get("tagline"):
        tl = sans(54)
        yy = int(H * 0.74)
        for ln in textwrap.wrap(meta["tagline"], 34):
            d.text((W / 2, yy), ln, font=tl, fill=(110, 100, 90), anchor="mm")
            yy += 78
    d.text((W / 2, int(H * 0.97)), "A clean, newly typeset edition", font=sans(38), fill=(255, 255, 255), anchor="mm")
    im.save(path_png)
    small = im.resize((160, 256), Image.LANCZOS)
    small.save(str(path_png).replace("1600x2560", "160x256"))
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=88)
    return buf.getvalue()


def pdf(meta, chs, out_pdf):
    from playwright.sync_api import sync_playwright
    font = (FONTS / "EBGaramond.ttf").resolve().as_uri()
    css = (f"@font-face{{font-family:'EB Garamond';src:url('{font}')}}" + CSS +
           "@page{size:6in 9in;margin:0.75in 0.55in 0.8in 0.75in}@page :left{margin-left:0.55in;margin-right:0.75in}"
           "body{margin:0;font-size:11.5pt}section{break-before:page}.titlepage h1{margin-top:2.2in}")
    parts = [f'<section class="titlepage"><p class="series">{esc(SERIES)}</p><h1>{esc(meta["title"])}</h1><p class="author">{esc(meta["author"])}</p></section>',
             "<section><h2>About this edition</h2>" + "".join(f"<p>{esc(p)}</p>" for p in meta["about"]) + "</section>",
             "<section><h2>Contents</h2>" + "".join(f'<p class="noindent">{esc(t)}</p>' for t, _ in chs) + "</section>"]
    parts += [f"<section>{b}</section>" for _, b in chs]
    page = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(parts)}</body></html>"
    tmp = out_pdf.with_suffix(".print.html")
    tmp.write_text(page, encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page()
        p.goto(tmp.resolve().as_uri())
        p.wait_for_timeout(500)
        p.pdf(path=str(out_pdf), width="6in", height="9in", display_header_footer=True, header_template="<span></span>",
              footer_template="<div style='width:100%;text-align:center;font-size:9px;color:#555'><span class='pageNumber'></span></div>",
              margin={"top": "0.75in", "bottom": "0.8in", "left": "0.7in", "right": "0.6in"})
        b.close()
    tmp.unlink()
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(out_pdf)).pages)
    except Exception:
        return len(re.findall(rb"/Type\s*/Page[^s]", out_pdf.read_bytes()))


def words(chs):
    return sum(len(BeautifulSoup(b, "lxml").get_text(" ").split()) for _, b in chs)


def flesch(chs):
    text = " ".join(BeautifulSoup(b, "lxml").get_text(" ") for _, b in chs)[:200000]
    sents = max(1, len(re.findall(r"[.!?]+\s", text)))
    ws = re.findall(r"[A-Za-z']+", text)
    syl = sum(max(1, len(re.findall(r"[aeiouy]+", w.lower())) - (1 if w.lower().endswith("e") and len(w) > 3 else 0)) for w in ws)
    return round(206.835 - 1.015 * len(ws) / sents - 84.6 * syl / max(1, len(ws)), 1)


def make(entry, out):
    out.mkdir(parents=True, exist_ok=True)
    raw = fetch(f"https://www.gutenberg.org/cache/epub/{entry['pg']}/pg{entry['pg']}-images.html")
    body = clean(raw.replace(b"\r", b""))
    chs = chapters(body)
    leftover = sum(b.lower().count("gutenberg") for _, b in chs)
    meta = dict(entry)
    meta["about"] = [
        (f"{entry['title']} by {entry['author']} was first published in {entry['year']}." if entry.get("year") else f"{entry['title']} is by {entry['author']}.") + " The text is in the public domain.",
        "This edition was newly set for easy reading on phones, e-readers and in print: clean chapter breaks, a working table of contents, consistent typography and no leftover scanning notes.",
        "Spelling and wording follow the original. Nothing in this book is financial, legal or medical advice; it is a historical text, read it as such.",
        "Edition design, cover and front matter by Snoutsmith Books.",
    ]
    total = sum(len(BeautifulSoup(b, "lxml").get_text(" ").split()) for _, b in chs)
    meta["about"].append(f"Reader's guide: {len(chs)} chapters, about {total:,} words – roughly {max(1, round(total / 250 / 60, 1))} hours at 250 words a minute.")
    for t, b in chs:
        w = len(BeautifulSoup(b, "lxml").get_text(" ").split())
        meta["about"].append(f"{t} – {w:,} words, about {max(1, round(w / 250))} min.")
    jpg = cover(meta, out / "cover-1600x2560.png")
    n_ch = build_epub(meta, chs, jpg, out / f"{entry['slug']}.epub")
    pages = pdf(meta, chs, out / f"{entry['slug']}-6x9.pdf")
    stats = {"chapters": n_ch, "words": words(chs), "pdf_pages": pages, "flesch": flesch(chs), "gutenberg_mentions_left": leftover}
    write_docs(entry, out, stats)
    return stats


STOP_END = {"of", "and", "the", "a", "an", "or", "to", "in", "on", "for", "with", "by"}


def common_name(t, n=40):
    """Name readers use: 'An Inquiry into the Nature and Causes of the Wealth of Nations' -> 'The Wealth of Nations'.
    Order: the part before ':'/';'/' – '; the phrase after the last ' the '; then whole words, never ending on of/and/the/a."""
    t = " ".join(t.split())
    if len(t) <= n:
        return t
    for sep in (":", ";", " – ", " - ", ", or ", "; or"):
        head = t.split(sep)[0].strip()
        if sep in t and 2 <= len(head.split()) and len(head) <= n:
            return head
    low = t.lower()
    i = low.rfind(" the ")
    if i > 0:
        tail = "The " + t[i + 5:].strip()
        if len(tail.split()) >= 3 and len(tail) <= n and " of " in tail.lower():   # "The Wealth of Nations"-type common names
            return tail
    words = []
    for w in t.split():
        if len(" ".join(words + [w])) > n:
            break
        words.append(w.rstrip(","))
        if w.endswith(","):
            break   # a clause ends here: "Principles of Political Economy, Abridged ..." -> "Principles of Political Economy"
    while words and words[-1].lower().strip(",.;:") in STOP_END:
        words.pop()
    return " ".join(words) or t[:n]


def short_title(t, n):
    return common_name(t, n)


def tidy(name):
    name = name.strip().rstrip(",;:.- ").strip()
    w = name.split()
    return " ".join(x if (i and x.lower() in STOP_END) else x[:1].upper() + x[1:] for i, x in enumerate(w))


def write_docs(e, out, st):
    name = e.get("short") or tidy(common_name(e["title"], 40))
    title = f"{name} – Clean Edition"
    (out / "meta.json").write_text(json.dumps({"free": True, "epub": f"{e['slug']}.epub", "xuong": "sach", "price": 0, "license": f"Public Domain – {e['title']} ({e['year']})", "stats": st}, indent=2), encoding="utf-8")
    (out / "LICENSES.md").write_text(
        f"# LICENSES\n\n| Asset | Source | License |\n|---|---|---|\n"
        f"| Text of *{e['title']}* by {e['author']} ({e['year']}) | Project Gutenberg eBook #{e['pg']} (https://www.gutenberg.org/ebooks/{e['pg']}), marked 'Public domain in the USA' | Public Domain. Per the Project Gutenberg License (sections 1.C and 1.E), once every reference to Project Gutenberg and its license is removed the public-domain text may be redistributed freely; this edition removes them and credits the source here only |\n"
        f"| Cover, title page, \"About this edition\", typesetting | Made by Snoutsmith Books (xuong-sach pipeline) | Own work |\n"
        f"| EB Garamond font (embedded in PDF/EPUB styling) | github.com/google/fonts | SIL Open Font License 1.1 (OFL) |\n"
        f"| Inter font (cover labels) | github.com/google/fonts | SIL Open Font License 1.1 (OFL) |\n\n"
        "The archive's name, trademark and license text were removed from this edition as its license requires for redistribution; "
        "only the public-domain text remains.\n", encoding="utf-8")
    (out / "CREDITS.md").write_text(f"# Credits\n\nBased on *{e['title']}* by {e['author']} ({e['year']}, Public Domain). "
                                   f"Source text: Project Gutenberg eBook #{e['pg']} (volunteer transcription; their trademark and license removed from the edition itself).\n", encoding="utf-8")
    store = [f"# {title}", "", f"Title ({len(title)} chars): **{title}**", "",
             f"{e['pitch']} This clean edition reads well on any phone, Kindle or in print.", "",
             f"- The complete original text of {e['title']} ({e['year']})",
             "- Newly typeset: clear chapters, working table of contents, no scanning clutter",
             "- EPUB for e-readers and phones, plus a print-ready 6×9 in PDF",
             f"- {st['chapters']} chapters · about {st['words']:,} words · {st['pdf_pages']} printed pages",
             "- Free: public-domain text, no DRM", "",
             "## What you get", "", f"- `{e['slug']}.epub` (EPUB 3)", f"- `{e['slug']}-6x9.pdf` ({st['pdf_pages']} pages)", "", "## FAQ", "",
             "**Is this the full book?** Yes, the complete original text.",
             "", "**Why is it free?** The text is in the public domain; we charge nothing for this clean edition.",
             "", "**Can I read it on Kindle?** Yes. Send the EPUB with Send to Kindle, or open it in any e-reader app.",
             "", "**Is the wording modernised?** No. Spelling and wording follow the original.",
             "", "**Is this financial advice?** No. It is a historical text; read it as such.", "",
             f"## Price\n\n0 USD (KHUON-NHA-MAY mục 8: public-domain text, light edit only). Leaders sell the same classics for 0.99–2.99 USD on Kindle; ours is a lead magnet for the paid Snoutsmith Books titles.",
             "", "## Label", "", f"Based on *{e['title']}* by {e['author']} (Public Domain). No AI-generated text in the book; cover and front matter made with code.",
             "", "## Tags", "", ", ".join(e["tags"])]
    (out / "STORE.md").write_text("\n".join(store) + "\n", encoding="utf-8")
    (out / "BAN-GIAO.md").write_text(
        f"# Bàn giao: {title} (miễn phí, sách công cộng)\n\n- Xưởng: Sách (`xuong-sach`) → books.snoutsmith.com · giá 0 USD · ngày {datetime.date.today():%d/%m/%Y}\n"
        f"- Tệp: `{e['slug']}.epub`, `{e['slug']}-6x9.pdf`, `cover-1600x2560.png` (+ `cover-160x256.png` thử đọc tên ở cỡ nhỏ)\n"
        f"- Số đo: {st['chapters']} chương · {st['words']:,} chữ · PDF {st['pdf_pages']} trang 6×9 in · Flesch {st['flesch']} (văn gốc, không sửa chữ) · còn {st['gutenberg_mentions_left']} chữ 'Gutenberg' trong sách\n"
        f"- Lên kệ: `n24tim_add([... 'price'=>0, 'license'=>'Public Domain – {e['title']} ({e['year']})' ])`; trang sản phẩm ghi \"Based on {e['title']} by {e['author']} (Public Domain)\".\n"
        "- Cửa 0: `CUA0.json` · Cửa 1 nhanh (≥ 70): `CUA1.json`.\n- Gỡ: xóa sản phẩm khỏi kệ; không có gì cài trên máy khách.\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("pg", type=int)
    a.add_argument("--out", default="")
    x = a.parse_args()
    cat = json.loads((K / "sach-cong-cong.json").read_text(encoding="utf-8"))
    e = next(c for c in cat if c["pg"] == x.pg)
    out = Path(x.out) if x.out else ROOT / "HANG" / f"{datetime.date.today():%Y%m%d}-{e['slug']}"
    print(json.dumps(make(e, out), ensure_ascii=False))
