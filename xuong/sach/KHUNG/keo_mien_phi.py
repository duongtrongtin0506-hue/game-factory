"""Daily free pull (KHUON-NHA-MAY mục 8): build the next public-domain classic from sach-cong-cong.json that is not
in HANG/ yet. python KHUNG/keo_mien_phi.py [--all]"""
import datetime
import json
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
sys.path.insert(0, str(K))
import sach  # noqa: E402

ROOT = K.parent


def todo():
    have = {p.name.split("-", 1)[1] for p in (ROOT / "HANG").glob("*-*") if p.is_dir()}
    return [e for e in json.loads((K / "sach-cong-cong.json").read_text(encoding="utf-8")) if e["slug"] not in have]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    queue = todo()
    if not queue:
        print("hết sách trong danh mục – thêm vào KHUNG/sach-cong-cong.json")
        return
    for e in (queue if "--all" in sys.argv else queue[:1]):
        out = ROOT / "HANG" / f"{datetime.date.today():%Y%m%d}-{e['slug']}"
        st = sach.make(e, out)
        line = f"| {datetime.date.today():%d/%m} | kéo miễn phí: {e['title']} | {st['chapters']} chương, {st['words']:,} chữ, PDF {st['pdf_pages']} tr |"
        nk = ROOT / "NHAT-KY.md"
        nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
        print(e["slug"], json.dumps(st))


if __name__ == "__main__":
    main()
