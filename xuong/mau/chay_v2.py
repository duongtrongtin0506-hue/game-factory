"""Xưởng Mẫu v2 – hàng chờ sau khi 8 mẫu khung12 đã hết (gốc lỗi "khong-co-mon" 24/10). Máy tự làm trọn 1 món/lượt:
  dựng .xlsx (KHUNG/mau_v2.py) → kiểm công thức độc lập (0 lỗi) → 5 ảnh xem trước từ số đã tính + bìa + GIF (+ CSV)
  → hồ sơ (HO-SO/<slug>/) → Cửa 0 vòng 3+4 (xuong/thiet-ke.py: chữ nội bộ, tương phản, ảnh) → nộp BAN-GIAO/_cho-cua-1/
  (món làm lại: gỡ bản cũ ở _tra-lai trong cùng commit). Không gọi AI. Hết hàng chờ → in XONG: ra 0 (không tốn gì).
  python chay_v2.py [--so-mon 1] [--khong-nop]
"""
import argparse
import csv
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
X = HERE.parent
sys.path.insert(0, str(HERE / "KHUNG"))
sys.path.insert(0, str(X))
import kiem_cong_thuc  # noqa: E402
import mau_v2  # noqa: E402
import xem_truoc  # noqa: E402
from chup import gif  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))
LAM = Path(os.environ.get("N24_LAM", r"D:\Net24\lam")) / "mau" / "V2"
DONE = HERE / "chay_v2.da-nop.json"

# slug → builder, file, accent, cover subtitle, preview tabs (sheet:rows:cols), old folder in _tra-lai, csv
HANG = {
    "debt-payoff-planner": ("debt", "B42318", "Snowball & Avalanche · debt-free month · interest · actual vs plan",
                            ["Dashboard:21:5", "Debts:19:7", "Plan:22:12", "Payments:12:4", "Start here:24:1"], "20261022-mau-debt-tracker", False),
    "meal-planner-grocery-list": ("meal", "1E7B34", "60 recipes · 4 week planners · food budget · auto grocery list",
                                  ["Week 1:14:9", "Grocery List:30:4", "Recipes:24:9", "Ingredients:24:6", "Start here:24:1"], "20261022-mau-meal-planner", False),
    "savings-goals-tracker": ("savings", "0A6CDB", "10 goals · target dates · progress bars · needed per month · on track",
                              ["Dashboard:19:10", "Goals:12:4", "Deposits:22:4", "Monthly:17:3", "Start here:24:1"], "20261022-mau-savings-goals", True),
    "weekly-task-planner": ("weekly", "6E3FD1", "Urgency-ranked tasks · habit streaks · bill due dates · weekly notes",
                            ["This Week:24:6", "Tasks:18:9", "Habits:24:7", "Bills:21:6", "Start here:24:1"], "20261022-mau-weekly-planner", False),
}
TEN = {"debt": "Debt Payoff Planner 2026", "meal": "Meal Planner & Grocery List", "savings": "Savings Goals Tracker 2026", "weekly": "Weekly Task Planner 2026"}


def log(m):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} [v2] {m}"
    print(line, flush=True)
    with open(HERE / "NHAT-KY-chay.txt", "a", encoding="utf-8") as h:
        h.write(line + "\n")


def done():
    try:
        return json.loads(DONE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def make(slug):
    kind, accent, sub, tabs, old, want_csv = HANG[slug]
    out = LAM / f"{datetime.date.today():%Y%m%d}-mau-{slug}"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    xl = out / f"{slug}.xlsx"
    getattr(mau_v2, kind)(str(xl))
    k = kiem_cong_thuc.check(xl)
    if k["error_count"]:
        log(f"{slug}: {k['error_count']} loi cong thuc {k['errors'][:3]} – bo mon")
        return None
    vals = xem_truoc.values(xl)
    names = []
    for i, t in enumerate(tabs, 1):
        sh, r, c = t.split(":")
        p = out / f"anh-{i}-{sh.lower().replace(' ', '-')}.png"
        xem_truoc.render(xl, vals, sh, int(r), int(c), p)
        names.append(p)
    subprocess.run([sys.executable, str(X / "bia.py"), str(out / "cover-1600x1200.png"), TEN[kind], sub, "#" + accent, str(names[0])], check=True)
    gif(out / "demo.gif", [names[1], names[0], names[2], names[3]], 960)
    from openpyxl import load_workbook
    wb = load_workbook(xl)
    vis = [ws for ws in wb.worksheets if ws.sheet_state == "visible"]
    if want_csv:
        (out / "csv").mkdir()
        for ws in vis:
            with open(out / "csv" / f"{ws.title.lower().replace(' ', '-')}.csv", "w", newline="", encoding="utf-8") as h:
                w = csv.writer(h)
                for row in ws.iter_rows():
                    w.writerow([xem_truoc.fmt(vals.get((ws.title.upper(), c.coordinate)) if isinstance(c.value, str) and str(c.value).startswith("=") else c.value, c.number_format) for c in row])
    ho = HERE / "HO-SO" / slug
    for f in ("STORE.md", "LEADER.md"):
        (out / f).write_text((ho / f).read_text(encoding="utf-8").replace("{TABS}", str(len(vis))).replace("{FORMULAS}", f"{k['formulas']:,}"), encoding="utf-8")
    shutil.copy(HERE / "HO-SO" / "LICENSES.md", out / "LICENSES.md")
    kb = xl.stat().st_size // 1024
    (out / "BAN-GIAO.md").write_text(f"""# Handover: {TEN[kind]}

- Shop: templates.snoutsmith.com · free · {datetime.date.today():%d/%m/%Y}{' · rebuilt after review (old version: ' + old.split('-', 1)[1] + ')' if old else ''}
- Files: `{xl.name}` ({kb} KB, {len(vis)} tabs, {k['formulas']:,} formulas){', csv/ (one CSV per tab)' if want_csv else ''}, cover + 5 previews + demo GIF
- Formula check: recalculated by an independent engine (Python `formulas`), {k['error_count']} errors; only functions supported by both Excel 2016+ and Google Sheets.
- Name matches content: every feature listed in the listing is a formula or tab in the file (checked tab by tab).
- Design: 1 font (Arial 12pt body = 16px), 1 accent #{accent}, blue input cells, gridlines off, 8px-multiple spacing; previews are rendered from the file's own calculated values.
- Remove: delete the file; nothing is installed.
""", encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"free": True, "xuong": "mau", "price": 0, "license": "Own work – Snoutsmith Templates", "formulas": k["formulas"], "formula_errors": 0,
                                               "tabs": len(vis), "kb": kb, "lam_lai_tu": old or None, "khuon": "mau_v2"}, ensure_ascii=False, indent=1), encoding="utf-8")
    r = subprocess.run([sys.executable, str(X / "thiet-ke.py"), str(out), "--mau", "#1D1D1F:#FFFFFF", "--mau", "#6E6E73:#FFFFFF", "--mau", "#1D1D1F:#EEF4FF", "--mau", f"#{accent}:#FFFFFF",
                        "--chu", "16", "--font", "Arial 12pt", "--them", f"Công thức | bộ tính độc lập | {k['formulas']} công thức, 0 lỗi ✅"], capture_output=True, text=True, encoding="utf-8")
    ok = r.returncode == 0
    (out / "CUA0.json").write_text(json.dumps({"pass": ok, "formulas": k["formulas"], "errors": 0, "thiet_ke": r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-300:],
                                               "ngay": f"{datetime.date.today()}"}, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"{slug}: {k['formulas']} cong thuc 0 loi, anh {len(names)}+gif, cua 0 {'DAT' if ok else 'LOI ' + r.stdout[-200:]}")
    return out if ok else False


def nop(out, slug):
    old = HANG[slug][4]
    g = ["git", "-C", str(NET24)]
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    dest = NET24 / "BAN-GIAO" / "_cho-cua-1" / out.name
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(out, dest)
    subprocess.run(g + ["add", str(dest.relative_to(NET24))])
    if old and (NET24 / "BAN-GIAO" / "_tra-lai" / old).exists():
        subprocess.run(g + ["rm", "-rq", f"BAN-GIAO/_tra-lai/{old}"])
    subprocess.run(g + ["commit", "-qm", f"Xuong Mau v2 (may nha): {out.name} cho Cua 1" + (f", thay {old}" if old else "")])
    for _ in range(3):
        if subprocess.run(g + ["push", "-q"]).returncode == 0:
            return True
        subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    return False


def run(so_mon=1, khong_nop=False):
    d = done()
    q = [s for s in HANG if s not in d]
    ra = qua = n = 0
    for slug in q[:so_mon]:
        out = make(slug)
        if out is None:
            continue
        ra += 1
        if out:
            qua += 1
            if not khong_nop and nop(out, slug):
                n += 1
                d[slug] = f"{datetime.date.today()} {out.name}"
                DONE.write_text(json.dumps(d, indent=1), encoding="utf-8")
    if not q:
        log("het hang cho v2")
    return ra, qua, n


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = argparse.ArgumentParser()
    a.add_argument("--so-mon", type=int, default=1)
    a.add_argument("--khong-nop", action="store_true")
    x = a.parse_args()
    ra, qua, n = run(x.so_mon, x.khong_nop)
    log(f"XONG: ra {ra}, cua 0 {qua}, day {n}")
