"""Nối mạng (HIEN-CHUONG-TONG 2h): mồi hàng đã lên kệ qua tổng đài n24-moi-hub.

moi_len_ke(xuong, net24): every BAN-GIAO/<date>-<xuong>-<ten>/ that has NGHIEM-THU.md (= on the shelf) and was not
announced yet gets one announcement: POST https://coinnew24.com/wp-json/n24/v1/moi/dang (header X-N24-Key from env
N24_SITE_KEY) with {url, title, text, img}. No key on this machine -> the item is queued in
net24-he-thong/BAN-GIAO/_cho-moi.jsonl (one JSON per line, de-duplicated by url) for a GitHub job that has the key.
State: NHAT-KY/da-moi.json in the workshop folder. Never prints the key.
CLI: python tools/chung/moi.py <xuong> --net24 <path>
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HUB = "https://coinnew24.com/wp-json/n24/v1/moi/dang"


def _first_url(text):
    m = re.search(r"https://[a-z0-9.-]+\.snoutsmith\.com/[^\s)>\]`'\"]+", text)
    return m.group(0).rstrip(".,") if m else ""


def _title(folder):
    for name in ("STORE.md", "BAN-GIAO.md"):
        p = folder / name
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace").splitlines()[0].lstrip("# ").replace("Bàn giao: ", "").strip()
    return folder.name


def post(item):
    key = os.environ.get("N24_SITE_KEY", "")
    if not key:
        return False
    req = urllib.request.Request(HUB, data=json.dumps(item).encode(), headers={"Content-Type": "application/json", "X-N24-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print("[moi] hub:", type(e).__name__)
        return False


def queue(net24, item):
    q = Path(net24) / "BAN-GIAO" / "_cho-moi.jsonl"
    have = set()
    if q.exists():
        for line in q.read_text(encoding="utf-8").splitlines():
            try:
                have.add(json.loads(line)["url"])
            except Exception:
                pass
    if item["url"] in have:
        return False
    with open(q, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return True


def moi_len_ke(xuong, net24, extra=()):
    state_p = ROOT / "NHAT-KY" / "da-moi.json"
    state_p.parent.mkdir(exist_ok=True)
    done = set(json.loads(state_p.read_text(encoding="utf-8"))) if state_p.exists() else set()
    items = list(extra)
    for d in sorted((Path(net24) / "BAN-GIAO").glob(f"2*-{xuong}-*")):
        nt = d / "NGHIEM-THU.md"
        if not nt.exists():
            continue
        url = _first_url(nt.read_text(encoding="utf-8", errors="replace"))
        if url:
            img = next((str(p.name) for p in d.glob("cover-*.png")), "")
            items.append({"url": url, "title": _title(d), "text": f"New from the Snoutsmith {xuong} workshop: {_title(d)}", "img": img, "nguon": d.name})
    sent = queued = 0
    for it in items:
        if it["url"] in done:
            continue
        if post(it):
            sent += 1
        elif queue(net24, it):
            queued += 1
        done.add(it["url"])
    state_p.write_text(json.dumps(sorted(done), indent=1), encoding="utf-8")
    return {"moi": sent, "cho_moi": queued}


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("xuong")
    a.add_argument("--net24", required=True)
    x = a.parse_args()
    print(json.dumps(moi_len_ke(x.xuong, x.net24)))
