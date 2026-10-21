"""Xưởng Mẫu – chạy mỗi đêm trên máy nhà (Task Scheduler 01:00): python chay.py --so-mon 2

Luật giai đoạn 1 (học → chép cấu trúc → nhân bản), không cần Claude:
  1. hàng chờ = 8 mẫu của KHUNG/khung12.py (Ngân sách · Trả nợ · Tiết kiệm · Thói quen · Kế hoạch tuần · Bữa ăn · Tài sản ròng · Thuê bao)
  2. dựng .xlsx theo khung 12 tháng (Start here → Settings → Jan…Dec → Year + biểu đồ)
  3. kiểm công thức bằng bộ tính độc lập (0 lỗi, nếu lỗi thì bỏ món, ghi nhật ký)
  4. ảnh: KHUNG/anh2.py (bìa tranh Public Domain + 5 ảnh mockup nhiều màu + GIF)
  5. hồ sơ (BAN-GIAO, LEADER, LICENSES, STORE, meta) → Cửa 0 → đẩy net24-he-thong/BAN-GIAO/_cho-cua-1/ + push (GitHub chấm Cửa 1)
  6. mồi hàng đã lên kệ (tools/chung/moi.py); ghi NHAT-KY.md
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
import os as _os
HANG = Path(_os.environ.get("N24_LAM", r"D:\Net24\lam")) / "mau" / "HANG"   # bản dựng nặng ở ổ D, ổ C chỉ giữ kho git
HANG.mkdir(parents=True, exist_ok=True)
CAU_HINH = HERE / "cau-hinh.json"
sys.path.insert(0, str(HERE / "KHUNG"))
sys.path.insert(0, str(HERE / "tools" / "chung"))
import anh2  # noqa: E402
import khung12  # noqa: E402
import kiem_cong_thuc  # noqa: E402
import moi  # noqa: E402
import nhip  # noqa: E402

NET24 = Path(os.environ.get("NET24", r"C:\Users\Administrator\Documents\Net24-HeThong"))
ART = {"budget-planner": "market", "debt-tracker": "harbor", "savings-goals": "garden", "habit-tracker": "morning", "weekly-planner": "study",
       "meal-planner": "kitchen", "net-worth": "estate", "subscription-tracker": "music"}
LEADERS = """| # | Leader (Etsy, tìm "budget planner google sheets", 21/10) | Giá |
|---|---|---|
| 1 | Yearly Budget Google Sheets Spreadsheet – https://www.etsy.com/listing/1207678608 | 14.99 USD |
| 2 | Budget planner spreadsheet (monthly + annual dashboard) – https://www.etsy.com/listing/1886538911 | ~10–15 USD |
| 3 | Simple Annual Budget Planner – https://www.etsy.com/listing/1865708241 | ~10 USD |"""


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with open(HERE / "NHAT-KY-chay.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def docs(slug, spec, out, check, img):
    title = spec["title"]
    t60 = f"{title} – Google Sheets & Excel"
    t60 = t60 if len(t60) <= 60 else title
    credit = {}
    if (out / "COVER-CREDIT.json").exists():
        credit = json.loads((out / "COVER-CREDIT.json").read_text(encoding="utf-8"))
    (out / "meta.json").write_text(json.dumps({"free": True, "xuong": "mau", "price": 0, "license": "Own work – Snoutsmith Templates", "khung": "12 thang",
                                               "formulas": check["formulas"], "formula_errors": check["error_count"], "images": img}, indent=2), encoding="utf-8")
    (out / "LEADER.md").write_text(f"# LEADER – {title}\n\n{LEADERS}\n\n## Checklist cấu trúc đã chép (11 điểm, xem KHUNG/khung12.py)\n\n"
                                   "| # | Đặc điểm leader | Bản mình |\n|---|---|---|\n"
                                   "| 1 | Tab hướng dẫn | ✅ Start here |\n| 2 | Tab cài đặt danh mục | ✅ Settings (≤ 20 dòng) |\n| 3 | 12 tab tháng cùng bố cục | ✅ Jan–Dec |\n"
                                   "| 4 | Thẻ số tổng đầu tháng | ✅ |\n| 5 | Danh sách thả xuống từ cài đặt | ✅ |\n| 6 | Tab tổng năm kéo từ 12 tháng | ✅ Year |\n"
                                   "| 7 | Biểu đồ năm | ✅ |\n| 8 | Dữ liệu mẫu | ✅ Jan–Oct |\n| 9 | Google Sheets + Excel | ✅ 1 tệp .xlsx |\n| 10 | Ô nhập tô màu, công thức khóa mềm | ✅ |\n\n"
                                   "Điểm vượt (giai đoạn 2, khi có số đo): bản 50/30/20, lịch hóa đơn, theo dõi nợ trong cùng tệp.\n", encoding="utf-8")
    (out / "LICENSES.md").write_text("# LICENSES\n\n| Asset | Source | License |\n|---|---|---|\n"
                                     f"| `{slug}.xlsx` (layout, formulas, sample data, text) | Snoutsmith Templates – `xuong/mau/KHUNG/khung12.py` | Own work; buyer may use for personal and business use, no resale of the file |\n"
                                     "| Preview images and GIF | Rendered by `KHUNG/anh2.py` from the workbook's computed values | Own work |\n"
                                     + (f"| Cover painting | {credit.get('credit', '')} | Public Domain / CC0 (museum open-access API flags it public domain) |\n" if credit else "")
                                     + "| Fonts | None embedded | – |\n", encoding="utf-8")
    (out / "STORE.md").write_text("\n".join([
        f"# {t60}", "", f"Title ({len(t60)} chars): **{t60}**", "",
        f"{spec['what']} Opens in Google Sheets or Excel on a free account – no add-ons, no scripts.", "",
        "- 15 tabs: Start here, Settings, 12 month tabs and a Year dashboard",
        "- Totals and the year chart fill themselves – you only type the tinted cells",
        "- Dropdowns pull from your own lists on Settings",
        f"- {check['formulas']} formulas, 0 errors in an independent formula checker",
        "- Sample data for January–October so you see it working, easy to clear", "",
        "## What you get", "", f"- `{slug}.xlsx` (Google Sheets: File → Import; Excel: open)", "- 6 preview images + demo GIF", "",
        "## FAQ", "", "**Do I need a paid Google or Microsoft plan?** No, free Google Sheets and Excel work.", "",
        "**Can I use it for 2027?** Yes – rename the month tabs' titles and clear the data.", "",
        "**How do I remove the sample data?** Select the tinted rows on each month and press Delete (Start here explains).", "",
        "**Can I change the categories?** Yes, on Settings; every month picks them up.", "",
        "**Does it work on a phone?** Yes, in the Google Sheets or Excel app.", "",
        "## Price", "", "0 USD now (lead magnet, KHUON-NHA-MAY mục 8). Leaders sell the same structure for 10–15 USD on Etsy.", "",
        "## Label", "", "Made with AI assistance (built by code; formulas checked by an independent engine).", "",
        "## Tags", "", ", ".join([slug.replace("-", " "), "google sheets", "excel", "2026 planner", "spreadsheet template"])]) + "\n", encoding="utf-8")
    (out / "BAN-GIAO.md").write_text(
        f"# Bàn giao: {t60}\n\n- Xưởng: Mẫu → templates.snoutsmith.com · giá 0 USD · {datetime.date.today():%d/%m/%Y}\n"
        f"- Tệp: `{slug}.xlsx` (15 tab), `cover-1600x1200.png`, 5 ảnh mockup `anh-*.png`, `demo.gif`\n"
        f"- Kiểm công thức (bộ tính độc lập): {check['formulas']} công thức, {check['error_count']} lỗi\n"
        "- Khung: học 3 leader Etsy (LEADER.md) → chép cấu trúc 12 tháng → nhân bản 8 chủ đề.\n", encoding="utf-8")


def make(slug):
    spec = dict(khung12.SPECS[slug])
    out = HANG / f"{datetime.date.today():%Y%m%d}-{slug}"
    shutil.rmtree(out, ignore_errors=True)
    path = out / f"{slug}.xlsx"
    khung12.build(spec, path)
    check = kiem_cong_thuc.check(path, ["YEAR!B17"])
    if check["error_count"]:
        log(f"{slug}: LOI CONG THUC {check['errors'][:2]} – bo mon")
        shutil.rmtree(out, ignore_errors=True)
        return None
    img = anh2.render(path, out, spec["title"], spec["tagline"], ART.get(slug))
    docs(slug, spec, out, check, img)
    for p in out.glob("*.kiem.json"):
        p.unlink()
    r = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(out), "--free"], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if r.returncode:   # Cua 0 do: chay lai 1 lan (loi tam thoi luc may ban)
        log('cua0 do, chay lai lan 2')
        r = subprocess.run([sys.executable, str(HERE / "tools/chung/cua0.py"), str(out), "--free"], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    log(f"{slug}: {check['formulas']} cong thuc, anh {img}, {r.stdout.strip()[:120]}")
    return r.returncode == 0


def day_cho_cua_1():
    g = ["git", "-C", str(NET24)]
    subprocess.run(g + ["pull", "-q", "--rebase", "--autostash"])
    sent = []
    for item in sorted(HANG.glob("2*-*")):
        if not item.is_dir() or (item / ".da-day").exists():
            continue
        try:
            if not json.loads((item / "CUA0.json").read_text(encoding="utf-8")).get("pass"):
                continue
        except Exception:
            continue
        date, _, name = item.name.partition("-")
        dest = NET24 / "BAN-GIAO" / "_cho-cua-1" / f"{date}-mau-{name}"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(item, dest, ignore=shutil.ignore_patterns("cua0-anh", "CUA1.json"))
        (item / ".da-day").write_text(f"{datetime.date.today()}", encoding="utf-8")
        sent.append(dest.name)
    if sent:
        subprocess.run(g + ["add", "BAN-GIAO/_cho-cua-1"])
        subprocess.run(g + ["commit", "-qm", f"Xuong Mau (may nha): {len(sent)} mau cho Cua 1"])
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
    have = {p.name.split("-", 1)[1] for p in HANG.glob("2*-*") if p.is_dir()}
    try:
        have |= set(json.loads(CAU_HINH.read_text(encoding="utf-8")).get("bo_qua", []))   # dieu-toc.py: chủ đề bị trả 2 lần
    except Exception:
        pass
    q = [s for s in khung12.SPECS if s not in have]
    ra = qua = 0
    for slug in q[:x.so_mon]:
        ok = make(slug)
        if ok is None:
            continue
        ra += 1
        qua += bool(ok)
    n = 0
    if not x.khong_nop:
        n = day_cho_cua_1()
        log("moi hang len ke: " + json.dumps(moi.moi_len_ke("mau", NET24)))
    if not q:
        log("het hang cho 8 mau – giai doan 1 du; them chu de vao khung12.SPECS khi co phieu")
    nk = HERE / "NHAT-KY.md"
    nk.write_text(nk.read_text(encoding="utf-8").rstrip("\n") + f"\n| {datetime.date.today():%d/%m} | {ra} mẫu | Cửa 0: {qua} | đẩy chờ Cửa 1: {n} | 0 | {ra - qua} |\n", encoding="utf-8")
    log(f"XONG: ra {ra}, cua 0 {qua}, day {n}")
    if not x.khong_nop and not _os.environ.get("N24_DIEU_TOC"):   # điều tốc tự ghi nhịp
        nhip.nhip("mau", ra)   # nhịp tim: 1 dòng/lần chạy vào 07-Nhat-ky/nha-may-nhip.log


if __name__ == "__main__":
    main()
