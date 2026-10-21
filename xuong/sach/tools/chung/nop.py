"""NỘP – hand every finished product to Agent 2: python tools/chung/nop.py <xuong> --net24 <net24-he-thong checkout>

A product is a folder HANG/<YYYYMMDD>-<ten>/. It is handed over only when CUA0.json and CUA1.json both say pass
and it has not been handed over before (marker .da-nop). Copies it to BAN-GIAO/<YYYYMMDD>-<xuong>-<ten>/ in the
net24-he-thong checkout and appends a line to TRANG-THAI/3-nha-may.md. Big files (> 50 MB) are skipped with a note.
Prints how many were handed over; the workflow then commits net24-he-thong and sends one Discord line.
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ok(p, name):
    try:
        return json.loads((p / name).read_text(encoding="utf-8")).get("pass") is True
    except Exception:
        return False


def main():
    a = argparse.ArgumentParser()
    a.add_argument("xuong")
    a.add_argument("--net24", required=True)
    x = a.parse_args()
    net = Path(x.net24)
    done = []
    for item in sorted((ROOT / "HANG").glob("*")):
        if not item.is_dir() or (item / ".da-nop").exists():
            continue
        if not (ok(item, "CUA0.json") and ok(item, "CUA1.json")):
            continue
        date, _, name = item.name.partition("-")
        dest = net / "BAN-GIAO" / f"{date}-{x.xuong}-{name}"
        if dest.exists():
            shutil.rmtree(dest)
        big = []
        def skip(d, names):
            out = []
            for n in names:
                p = Path(d) / n
                if p.is_file() and p.stat().st_size > 50e6:
                    out.append(n)
                    big.append(n)
            return out
        shutil.copytree(item, dest, ignore=skip)
        if big:
            (dest / "TEP-LON.md").write_text("Tệp > 50 MB để ở GitHub Releases của kho xưởng: " + ", ".join(big) + "\n", encoding="utf-8")
        (item / ".da-nop").write_text(datetime.date.today().isoformat(), encoding="utf-8")
        done.append(dest.name)
    if done:
        st = net / "TRANG-THAI" / "3-nha-may.md"
        if st.exists():
            line = f"- {datetime.date.today():%d/%m} [{x.xuong}] nộp {len(done)}: " + ", ".join(done)
            st.write_text(st.read_text(encoding="utf-8").rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
    print(json.dumps({"nop": len(done), "items": done}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
