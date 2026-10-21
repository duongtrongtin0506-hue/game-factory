"""Nhịp tim nhà máy: mỗi lịch Task Scheduler chạy xong ghi 1 dòng `<giờ> <xưởng> <số món>` vào
net24-he-thong/07-Nhat-ky/nha-may-nhip.log rồi commit + push (kiem-doc-lap đọc tệp; 26 giờ không có dòng = 🔴).
python tools/chung/nhip.py <xuong> <so_mon> [--net24 PATH]"""
import datetime
import os
import subprocess
import sys
from pathlib import Path

DEFAULT = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))


def nhip(xuong, so_mon, net24=DEFAULT):
    net24 = Path(net24)
    g = ["git", "-C", str(net24)]
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    log = net24 / "07-Nhat-ky" / "nha-may-nhip.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {xuong} {so_mon}\n")
    subprocess.run(g + ["add", "07-Nhat-ky/nha-may-nhip.log"])
    subprocess.run(g + ["commit", "-qm", f"nhip {xuong} {so_mon}"])
    for _ in range(3):   # concurrent nightly jobs: retry the push after a rebase
        if subprocess.run(g + ["push", "-q"]).returncode == 0:
            return True
        subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    return False


if __name__ == "__main__":
    nhip(sys.argv[1], sys.argv[2], sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--net24" else DEFAULT)
