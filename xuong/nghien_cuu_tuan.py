"""Nghiên cứu thứ Hai cho cả 6 xưởng – chạy bằng máy (Task Scheduler Net24\\NghienCuu, thứ Hai 07:00), không cần Claude.
python xuong/nghien_cuu_tuan.py  → net24-he-thong/13-Ban-hang-so/HOC-TOP/<nganh>.md (+ y-tuong khi có khóa AI) + commit + push.
Số liệu top 20 lấy từ trang công khai/API (CrazyGames, itch.io, WordPress.org, Gumroad, Gutenberg, Google Play)."""
import datetime
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))
TOOL = HERE / "sach" / "tools" / "chung" / "nghien_cuu.py"


def main():
    g = ["git", "-C", str(NET24)]
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    log = HERE / "NHAT-KY-nghien-cuu.txt"
    with open(log, "a", encoding="utf-8") as f:
        for nganh in ["game", "sach", "mau", "studio", "app", "tool"]:
            r = subprocess.run([sys.executable, str(TOOL), nganh, "--out", str(HERE / nganh / "NGHIEN-CUU"), "--net24", str(NET24)],
                               env=env, capture_output=True, text=True, encoding="utf-8", timeout=900)
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {nganh}: {(r.stdout.strip().splitlines() or ['?'])[-1]} {r.stderr.strip()[-200:]}\n")
    for path in ("13-Ban-hang-so/HOC-TOP", "BAN-GIAO/y-tuong"):
        if (NET24 / path).exists():
            subprocess.run(g + ["add", path])
    subprocess.run(g + ["commit", "-qm", f"Agent 3 (may nha): hoc top 6 xuong {datetime.date.today()}"])
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    subprocess.run(g + ["push", "-q"])
    sys.path.insert(0, str(HERE / "sach" / "tools" / "chung"))
    import nhip
    nhip.nhip("nghien-cuu", 6, NET24)


if __name__ == "__main__":
    main()
