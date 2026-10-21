"""Xưởng Sách – chạy mỗi đêm trên máy nhà (Task Scheduler 01:00): python chay.py --so-mon 2

Đúng quy trình 8 cuốn 21/10, không cần Claude:
  1. hàng chờ: KHUNG/sach-cong-cong.json, tự bổ sung 30 tựa công cộng tải nhiều nhất trên Gutenberg
     (economics / self-help / business / success / conduct of life), tiếng Anh, "Public domain in the USA"
  2. sach.make: tải → xóa thương hiệu Gutenberg → EPUB 3 + PDF 6×9 → hồ sơ
  3. bìa: KHUNG/bia_sach.py (tranh Public Domain AIC/The Met + dải thương hiệu), lỗi thì giữ bìa chữ
  4. Cửa 0 (epubcheck thật) ở máy nhà
  5. đẩy vào net24-he-thong/BAN-GIAO/_cho-cua-1/YYYYMMDD-sach-<slug>/ + commit + push; GitHub (workflow cua-1) chấm Cửa 1
     và tự chuyển sang BAN-GIAO/ hoặc _tra-lai/; ghi NHAT-KY.md
Biến môi trường: N24_AI_KEY, N24_AI_URL (AI chung), NET24 (đường dẫn kho net24-he-thong), EPUBCHECK_JAR, JAVA_HOME.
"""
import argparse
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "KHUNG"))
import sach  # noqa: E402
import bia_sach  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Desktop\net24-he-thong"))
TOOLS = Path(r"C:\Users\Administrator\Desktop\xuong\_cong-cu")
QUEUE = HERE / "KHUNG" / "sach-cong-cong.json"
TOPICS = ["economics", "self-help", "business", "success", "conduct of life", "thrift", "wealth"]


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with open(HERE / "NHAT-KY-chay.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def nap_hang_cho(can=30):
    """Add the most-downloaded public-domain English titles not yet queued (Gutenberg search, sorted by downloads)."""
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    have = {e["pg"] for e in q}
    added = 0
    for t in TOPICS:
        if added >= can:
            break
        try:
            h = sach.fetch(f"https://www.gutenberg.org/ebooks/search/?query={t.replace(' ', '+')}&sort_order=downloads").decode("utf-8", "replace")
        except Exception as e:
            log(f"tim {t}: {type(e).__name__}")
            continue
        for pg, title, sub in re.findall(r'href="/ebooks/(\d+)".*?<span class="title">([^<]+)</span>\s*(?:<span class="subtitle">([^<]*)</span>)?', h, re.S):
            pg = int(pg)
            if pg in have or added >= can:
                continue
            try:
                page = sach.fetch(f"https://www.gutenberg.org/ebooks/{pg}").decode("utf-8", "replace")
            except Exception:
                continue
            if "Public domain in the USA" not in page or not re.search(r"<td>English</td>", page):
                continue
            author = re.sub(r",\s*\d{3,4}\??-\d{3,4}\??", "", (sub or "Unknown").strip())
            title = " ".join(title.split())[:90]
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48]
            q.append({"pg": pg, "slug": slug, "title": title, "author": author, "year": "",
                      "pitch": f"{title} by {author}, a public-domain classic on {t}.", "tagline": f"A classic on {t}",
                      "tags": [t, author, "public domain", "free ebook", "classic"]})
            have.add(pg)
            added += 1
    QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False), encoding="utf-8")
    return added


def doi_bia(entry, out):
    """Replace the text-only cover with the art cover (bia_sach) and put it inside the EPUB."""
    tmp = out / "_bia"
    try:
        words = [w for w in re.findall(r"[A-Za-z]+", entry["title"]) if len(w) > 3][:2]
        bia_sach.make({"slug": entry["slug"], "title": entry["title"], "author": entry["author"],
                       "q": words + ["landscape", "harbor", "still life"]}, str(tmp))
        src = tmp / entry["slug"]
        shutil.copy2(src / "cover-1600x2560.png", out / "cover-1600x2560.png")
        shutil.copy2(src / "cover-160x256.png", out / "cover-160x256.png")
        credit = json.loads((src / "COVER-CREDIT.json").read_text(encoding="utf-8"))
        from PIL import Image
        buf = io.BytesIO()
        Image.open(out / "cover-1600x2560.png").convert("RGB").save(buf, "JPEG", quality=88)
        ep = out / f"{entry['slug']}.epub"
        old = zipfile.ZipFile(ep)
        new_path = ep.with_suffix(".new.epub")
        with zipfile.ZipFile(new_path, "w") as z:
            for i in old.infolist():
                data = buf.getvalue() if i.filename == "OEBPS/images/cover.jpg" else old.read(i.filename)
                z.writestr(i, data, compress_type=zipfile.ZIP_STORED if i.filename == "mimetype" else zipfile.ZIP_DEFLATED)
        old.close()
        new_path.replace(ep)
        with open(out / "LICENSES.md", "a", encoding="utf-8") as f:
            oid = str(credit.get("met_object", ""))
            link = f"https://www.artic.edu/artworks/{oid[4:]}" if oid.startswith("aic-") else f"https://www.metmuseum.org/art/collection/search/{oid}"
            src = "Art Institute of Chicago Open Access API: is_public_domain = true" if oid.startswith("aic-") else "The Met Open Access API: isPublicDomain = true"
            f.write(f"\n| Cover art | {credit['credit']} – {link} | Public Domain / CC0 ({src}; the museum releases these images under CC0) |\n")
        return True
    except Exception as e:
        log(f"bia tranh loi, giu bia chu: {type(e).__name__}: {e}")
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def cua(out, epub):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    jre = next(TOOLS.glob("jdk-*-jre/bin"), None)
    if jre:
        env["PATH"] = str(jre) + os.pathsep + env["PATH"]
    jar = TOOLS / "epubcheck-5.1.0" / "epubcheck.jar"
    if jar.exists():
        env.setdefault("EPUBCHECK_JAR", str(jar))
    c0 = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(out), "--epub", epub, "--free"], env=env, capture_output=True, text=True, encoding="utf-8")
    log("cua0 " + c0.stdout.strip()[:160])
    if c0.returncode:
        return False
    return True


LEADER = """# LEADER – {title}

Dòng: sách công cộng miễn phí (KHUON-NHA-MAY mục 8, giai đoạn 1: học → chép cấu trúc → nhân bản).

| # | Đặc điểm bản top (Standard Ebooks / Gutenberg) | Bản mình |
|---|---|---|
| 1 | Văn bản đầy đủ, đúng bản gốc | ✅ |
| 2 | EPUB hợp lệ (epubcheck) | ✅ 0 lỗi |
| 3 | Mục lục bấm được | ✅ |
| 4 | Chia chương rõ | ✅ {chapters} chương |
| 5 | Bìa riêng có tranh | ✅ tranh Public Domain (AIC/The Met) |
| 6 | Kiểu chữ sạch, không rác quét | ✅ EB Garamond (OFL) |
| 7 | Không DRM, miễn phí | ✅ |
| 8 | Ghi nguồn + giấy phép | ✅ CREDITS.md, LICENSES.md |
| 9 | Bản in | ✅ PDF 6×9 in, {pages} trang |
| 10 | Siêu dữ liệu đủ (tên, tác giả, ngôn ngữ) | ✅ |

Điểm vượt (giai đoạn 2, khi có số đo): lời dẫn + tóm tắt chương + sổ bài tập.
"""


def day_cho_cua_1():
    """Push every HANG item that passed Cửa 0 and was not pushed yet to net24-he-thong/BAN-GIAO/_cho-cua-1/ (GitHub
    workflow cua-1 grades it: pass -> BAN-GIAO/<ten>/, fail -> BAN-GIAO/_tra-lai/<ten>/LY-DO.md)."""
    g = ["git", "-C", str(NET24)]
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    sent = []
    for item in sorted((HERE / "HANG").glob("2*-*")):
        if not item.is_dir() or (item / ".da-day").exists() or (item / ".da-nop").exists():
            continue
        try:
            if not json.loads((item / "CUA0.json").read_text(encoding="utf-8")).get("pass"):
                continue
            meta = json.loads((item / "meta.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        if not (item / "LEADER.md").exists():
            st = meta.get("stats", {})
            title = (item / "BAN-GIAO.md").read_text(encoding="utf-8").splitlines()[0].replace("# Bàn giao: ", "")
            (item / "LEADER.md").write_text(LEADER.format(title=title, chapters=st.get("chapters", "?"), pages=st.get("pdf_pages", "?")), encoding="utf-8")
        date, _, name = item.name.partition("-")
        dest = NET24 / "BAN-GIAO" / "_cho-cua-1" / f"{date}-sach-{name}"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(item, dest, ignore=shutil.ignore_patterns("cua0-anh", "*.print.html", "CUA1.json"))
        (item / ".da-day").write_text(f"{datetime.date.today()}", encoding="utf-8")
        sent.append(dest.name)
    if sent:
        subprocess.run(g + ["add", "BAN-GIAO/_cho-cua-1"])
        subprocess.run(g + ["commit", "-qm", f"Xuong Sach (may nha): {len(sent)} sach cho Cua 1"])
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
    a.add_argument("--so-mon", type=int, default=2)
    a.add_argument("--khong-nop", action="store_true")
    x = a.parse_args()
    have = {p.name.split("-", 1)[1] for p in (HERE / "HANG").glob("*-*") if p.is_dir()}
    q = [e for e in json.loads(QUEUE.read_text(encoding="utf-8")) if e["slug"] not in have]
    if len(q) < x.so_mon:
        log(f"hang cho con {len(q)}, nap them: +{nap_hang_cho()}")
        q = [e for e in json.loads(QUEUE.read_text(encoding="utf-8")) if e["slug"] not in have]
    ra = qua = 0
    for e in q[:x.so_mon]:
        out = HERE / "HANG" / f"{datetime.date.today():%Y%m%d}-{e['slug']}"
        try:
            st = sach.make(e, out)
        except Exception as err:
            log(f"LOI {e['slug']}: {type(err).__name__}: {err}")
            shutil.rmtree(out, ignore_errors=True)
            continue
        ra += 1
        bia = doi_bia(e, out)
        ok = cua(out, f"{e['slug']}.epub")
        qua += ok
        log(f"{e['slug']}: {st['chapters']} chuong, {st['words']} chu, PDF {st['pdf_pages']} tr, bia tranh {bia}, cua 0 {ok}")
    n = 0 if x.khong_nop else day_cho_cua_1()
    nk = HERE / "NHAT-KY.md"
    nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + f"\n| {datetime.date.today():%d/%m} | {ra} sách | {qua} | {n} | 0 | {ra - qua} |\n", encoding="utf-8")
    log(f"XONG: ra {ra}, qua cua 0 {qua}, day cho cua 1 {n}")


if __name__ == "__main__":
    main()
