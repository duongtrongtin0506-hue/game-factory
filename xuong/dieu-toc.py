"""Điều tốc nhà máy – chạy MỖI LƯỢT trước chay.py của 1 xưởng (Task Scheduler mỗi 2 giờ): python xuong/dieu-toc.py <xuong>

Máy tự lo trọn vòng, không chờ Claude:
  0. Khóa lượt (D:/Net24/lam/<xuong>/.lock, quá 3 giờ coi như kẹt và gỡ) – lượt sau không chồng lượt trước.
  1. Máy bận (CPU > 80 % hoặc pin < 30 %) → bỏ lượt, ghi nhịp "bo-luot".
  2. TỰ SỬA 3 BẬC theo hàng bị Cửa 1 trả (net24-he-thong/BAN-GIAO/_tra-lai/<ngày>-<xuong>-<ten>/LY-DO.md):
     bậc 1: lần trả đầu → chỉnh xuong/<xuong>/cau-hinh.json trong khoảng cho phép (AI chung nếu có khóa; không có thì quy
            tắc từ khóa trong LY-DO) rồi làm lại món đó 1 lần (xóa bản dựng để chay.py dựng lại). AI không được sửa chay.py.
     bậc 2: bị trả lần 2 → thêm chủ đề vào "bo_qua", xưởng làm chủ đề kế.
     bậc 3: 3 chủ đề liền bị trả → quay cau-hinh.json về bản tốt gần nhất (bản lúc món gần nhất qua Cửa 1), ghi sổ tuần.
  3. Chạy chay.py --so-mon 1 (thử lại 1 lần nếu lỗi), đọc dòng "XONG" → nhịp tim 07-Nhat-ky/nha-may-nhip.txt:
     <giờ> <xưởng> <món> <cửa 0 đạt/lỗi>, commit + push.
  4. Dọn bản dựng tạm > 7 ngày trong D:/Net24/lam/<xuong>/ (không đụng HANG/ đã nộp).
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

X = Path(__file__).resolve().parent
NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))
LAM = Path(os.environ.get("N24_LAM", r"D:\Net24\lam"))
SAFE_KEYS = {"so_anh": (5, 8), "do_dai_mo_ta": (1, 3), "bieu_do": (0, 1), "huong_dan": (0, 1), "faq": (5, 8)}
DEFAULT_CFG = {"so_anh": 5, "do_dai_mo_ta": 1, "bieu_do": 1, "huong_dan": 1, "faq": 5, "bo_qua": [], "lan_tra": {}, "tra_lien": 0}


def now():
    return datetime.datetime.now()


def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
    return r.stdout.strip()


def busy():
    try:
        cpu = float(ps("(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average") or 0)
    except ValueError:
        cpu = 0
    bat = ps("(Get-CimInstance Win32_Battery).EstimatedChargeRemaining")
    low = bat.isdigit() and int(bat) < 30
    return cpu > 80 or low, f"cpu {cpu:.0f}% pin {bat or '-'}"


def git(*a):
    return subprocess.run(["git", "-C", str(NET24), *a], capture_output=True, text=True)


def nhip(xuong, mon, cua0):
    git("pull", "-q", "--rebase", "--autostash")
    f = NET24 / "07-Nhat-ky" / "nha-may-nhip.txt"
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "a", encoding="utf-8") as h:
        h.write(f"{now():%Y-%m-%d %H:%M} {xuong} {mon} {cua0}\n")
    git("add", "07-Nhat-ky/nha-may-nhip.txt")
    git("commit", "-qm", f"nhip {xuong} {mon} {cua0}")
    for _ in range(3):
        if git("push", "-q").returncode == 0:
            return
        git("pull", "-q", "--rebase", "--autostash")


def cfg_load(xuong):
    p = X / xuong / "cau-hinh.json"
    try:
        c = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        c = {}
    return {**DEFAULT_CFG, **c}


def cfg_save(xuong, c):
    (X / xuong / "cau-hinh.json").write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")


def so_tuan(line):
    f = NET24 / "07-Nhat-ky" / "nha-may-so-tuan.md"
    with open(f, "a", encoding="utf-8") as h:
        h.write(f"- {now():%d/%m %H:%M} {line}\n")
    git("add", "07-Nhat-ky/nha-may-so-tuan.md")


def ai_tune(ly_do, c):
    """Ask the shared AI for new values of the safe keys only; None if no AI key on this machine."""
    sys.path.insert(0, str(X / "sach" / "tools" / "chung"))
    try:
        import ai
        if not ai.available():
            return None
        r = ai.ask_json("A product was rejected by a review gate. Reasons:\n" + ly_do[:2000] + "\nCurrent settings: "
                        + json.dumps({k: c[k] for k in SAFE_KEYS}) + "\nAllowed ranges: " + json.dumps(SAFE_KEYS)
                        + "\nReturn JSON with new values for some of these keys only.", 400)
        return {k: int(v) for k, v in (r or {}).items() if k in SAFE_KEYS}
    except Exception:
        return None


def rule_tune(ly_do, c):
    t = ly_do.lower()
    out = {}
    if re.search(r"chart|graph|visual", t):
        out["bieu_do"] = 1
    if re.search(r"image|screenshot|preview|photo", t):
        out["so_anh"] = c["so_anh"] + 1
    if re.search(r"description|copy|marketing|position|explain|clarif", t):
        out["do_dai_mo_ta"] = c["do_dai_mo_ta"] + 1
    if re.search(r"guide|instruction|how to|onboard", t):
        out["huong_dan"] = 1
    if re.search(r"faq|question", t):
        out["faq"] = c["faq"] + 1
    return out or {"do_dai_mo_ta": c["do_dai_mo_ta"] + 1}


def tu_sua(xuong):
    """Read new rejections for this workshop and apply the 3 steps. Returns a short note."""
    c = cfg_load(xuong)
    notes = []
    for d in sorted((NET24 / "BAN-GIAO" / "_tra-lai").glob(f"2*-{xuong}-*")):
        ly = d / "LY-DO.md"
        if not ly.exists() or (d / ".da-xu-ly").exists():
            continue
        ten = d.name.split(f"-{xuong}-", 1)[1]
        lan = c["lan_tra"].get(ten, 0) + 1
        c["lan_tra"][ten] = lan
        c["tra_lien"] += 1
        text = ly.read_text(encoding="utf-8", errors="replace")
        if lan == 1:
            new = ai_tune(text, c) or rule_tune(text, c)
            for k, v in new.items():
                lo, hi = SAFE_KEYS[k]
                c[k] = max(lo, min(hi, int(v)))
            for b in (LAM / xuong / "HANG").glob(f"2*-{ten}"):
                shutil.rmtree(b, ignore_errors=True)   # chay.py dựng lại món này ở lượt này
            notes.append(f"bac1 {ten}: {new}")
        else:
            if ten not in c["bo_qua"]:
                c["bo_qua"].append(ten)
            notes.append(f"bac2 {ten}: bo qua")
        if c["tra_lien"] >= 3:
            tot = X / xuong / "cau-hinh.tot.json"
            if tot.exists():
                good = json.loads(tot.read_text(encoding="utf-8"))
                c = {**c, **{k: good[k] for k in SAFE_KEYS if k in good}}
            c["tra_lien"] = 0
            notes.append("bac3: quay cau hinh tot gan nhat")
            so_tuan(f"[{xuong}] 3 món liền bị trả – đã quay cấu hình tốt gần nhất, bỏ qua: {', '.join(c['bo_qua'][-3:])}")
        (d / ".da-xu-ly").write_text(now().isoformat(), encoding="utf-8")
    # a fresh pass since last run resets the streak and becomes the "known good" settings
    passed = [p for p in (NET24 / "BAN-GIAO").glob(f"2*-{xuong}-*") if (p / "CUA1.json").exists()]
    if passed:
        newest = max(p.stat().st_mtime for p in passed)
        if newest > c.get("lan_dat", 0):
            c["lan_dat"] = newest
            c["tra_lien"] = 0
            (X / xuong / "cau-hinh.tot.json").write_text(json.dumps({k: c[k] for k in SAFE_KEYS}, indent=1), encoding="utf-8")
    cfg_save(xuong, c)
    return "; ".join(notes)


def don_tam(xuong):
    cut = time.time() - 7 * 86400
    n = 0
    for p in (LAM / xuong).glob("*"):
        if p.name in ("HANG", ".lock"):
            continue
        if p.stat().st_mtime < cut:
            shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
            n += 1
    return n


def main():
    xuong = sys.argv[1]
    so_mon = sys.argv[2] if len(sys.argv) > 2 else "1"
    base = LAM / xuong
    base.mkdir(parents=True, exist_ok=True)
    lock = base / ".lock"
    if lock.exists() and time.time() - lock.stat().st_mtime < 3 * 3600:
        print("dang co luot khac – bo qua")
        return
    lock.write_text(str(os.getpid()))
    try:
        b, why = busy()
        if b:
            nhip(xuong, 0, "bo-luot " + why.replace(" ", "_"))
            return
        git("pull", "-q", "--rebase", "--autostash")
        note = tu_sua(xuong)
        env = dict(os.environ, PYTHONIOENCODING="utf-8", N24_DIEU_TOC="1")
        out = ""
        for lan in (1, 2):
            r = subprocess.run([sys.executable, "chay.py", "--so-mon", so_mon], cwd=str(X / xuong), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
            out = r.stdout + r.stderr
            if r.returncode == 0:
                break
        m = re.search(r"XONG: ra (\d+), (?:qua )?cua 0 (\d+)", out)
        mon, ok = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
        cua0 = "loi-chay" if not m else ("dat" if mon and ok == mon else "loi" if mon else "khong-co-mon")
        don = don_tam(xuong)
        nhip(xuong, mon, cua0 + (f" tu-sua[{note}]" if note else "") + (f" don{don}" if don else ""))
        print(xuong, mon, cua0, note)
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
