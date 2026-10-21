"""Xưởng Sách – chạy mỗi đêm trên máy nhà (Task Scheduler 01:00): python chay.py --so-mon 2

Đúng quy trình 8 cuốn 21/10, không cần Claude:
  1. hàng chờ: KHUNG/sach-cong-cong.json, tự bổ sung 30 tựa công cộng tải nhiều nhất trên Gutenberg
     (economics / self-help / business / success / conduct of life), tiếng Anh, "Public domain in the USA"
  2. sach.make: tải → xóa thương hiệu Gutenberg → EPUB 3 + PDF 6×9 → hồ sơ
  3. bìa: KHUNG/bia_sach.py (tranh Public Domain AIC/The Met + dải thương hiệu), lỗi thì giữ bìa chữ
  4. Cửa 0 (epubcheck thật) → Cửa 1 (AI chung chấm 4 vai, không có khóa = không nộp)
  5. nộp: chép vào net24-he-thong/BAN-GIAO/YYYYMMDD-sach-<slug>/ + commit + push; ghi NHAT-KY.md
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
            f.write(f"\n| Cover art | {credit['credit']} | Public Domain (CC0) |\n")
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
    c1 = subprocess.run([sys.executable, str(HERE / "tools/chung/cua1.py"), str(out), "--free"], env=env, capture_output=True, text=True, encoding="utf-8")
    log("cua1 " + c1.stdout.strip()[:160])
    return c1.returncode == 0


def nop():
    r = subprocess.run([sys.executable, str(HERE / "tools/chung/nop.py"), "sach", "--net24", str(NET24)], capture_output=True, text=True, encoding="utf-8")
    log("nop " + r.stdout.strip()[:300])
    res = json.loads(r.stdout or '{"nop":0}')
    if res.get("nop"):
        g = ["git", "-C", str(NET24)]
        subprocess.run(g + ["add", "BAN-GIAO", "TRANG-THAI/3-game.md"])
        subprocess.run(g + ["commit", "-qm", f"Xuong Sach (may nha): nop {res['nop']} sach"])
        subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
        subprocess.run(g + ["push", "-q"])
    return res.get("nop", 0)


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
        log(f"{e['slug']}: {st['chapters']} chuong, {st['words']} chu, PDF {st['pdf_pages']} tr, bia tranh {bia}, qua cua {ok}")
    n = 0 if x.khong_nop else nop()
    nk = HERE / "NHAT-KY.md"
    nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + f"\n| {datetime.date.today():%d/%m} | {ra} sách | {qua} | {n} | 0 | {ra - qua} |\n", encoding="utf-8")
    log(f"XONG: ra {ra}, qua cua {qua}, nop {n}")


if __name__ == "__main__":
    main()
