"""Ảnh bán hàng cho 1 mẫu 12 tháng (Cửa thẩm mỹ: nhiều màu, mockup thiết bị, ≥ 5 ảnh + 1 GIF, bìa có tranh):
python KHUNG/anh2.py <file.xlsx> <out-dir> "<Title>" "<tagline>"
  1 cover-1600x1200.png      tranh Public Domain (AIC/The Met, qua bia_sach.find_art) + dải thương hiệu + laptop hiện tab Year
  2 anh-2-thang-laptop.png   tab tháng 1 trong laptop
  3 anh-3-nam-bieu-do.png    tab Year + biểu đồ vẽ từ số đã tính
  4 anh-4-cai-dat-tablet.png tab Settings trong máy tính bảng
  5 anh-5-dien-thoai.png     thẻ số + danh sách tháng trên điện thoại
  6 anh-6-ben-trong.png      "Có gì bên trong": 15 tab
  demo.gif                   ảnh 2→5 lặp, 800×600
Mọi số trong ảnh lấy từ chính tệp đã tính bằng bộ tính độc lập (không vẽ số giả). Ghi công tranh vào COVER-CREDIT.json.
"""
import base64
import html
import io
import json
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

K = Path(__file__).resolve().parent
sys.path.insert(0, str(K))
import kiem_cong_thuc  # noqa: E402,F401
import formulas  # noqa: E402

ACCENT = "#E8833A"
PALETTE = ["#E8833A", "#2B4A3B", "#4F7CAC", "#C8553D", "#8E6C8A", "#E0A458"]


def compute(path):
    sol = formulas.ExcelModel().loads(str(path)).finish().calculate()
    vals = {}
    for key, rng in sol.items():
        k = key.split("]")[-1].replace("'", "")
        if "!" in k and ":" not in k:
            try:
                vals[k.upper()] = rng.value.ravel()[0]
            except Exception:
                pass
    return vals


def fmt(v, nf):
    if v is None or str(v) in ("empty", "None", ""):
        return ""
    try:
        f = float(v)
    except Exception:
        return html.escape(str(v))
    if "%" in nf:
        return f"{f * 100:.0f}%"
    if "$" in nf:
        return f"${f:,.0f}" if abs(f) >= 1000 else f"${f:,.2f}"
    if "yy" in nf or "dd" in nf:
        import datetime
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(f))).strftime("%b %d")
    return f"{f:,.0f}" if f == int(f) else f"{f:,.2f}"


def table(wb, vals, sheet, rows=24, cols=8, start=1):
    import datetime
    ws = wb[sheet]
    out = []
    for r in range(start, min(ws.max_row, start + rows - 1) + 1):
        cells = []
        for c in range(1, min(ws.max_column, cols) + 1):
            cell = ws.cell(row=r, column=c)
            v = cell.value
            if isinstance(v, str) and v.startswith("="):
                v = vals.get(f"{sheet.upper()}!{get_column_letter(c)}{r}", "")
            elif isinstance(v, datetime.datetime):
                v = (v.date() - datetime.date(1899, 12, 30)).days
            elif isinstance(v, datetime.date):
                v = (v - datetime.date(1899, 12, 30)).days
            bg = cell.fill.fgColor.rgb if cell.fill and cell.fill.fill_type == "solid" else None
            st = f"background:#{bg[-6:]};" if isinstance(bg, str) and len(bg) >= 6 else ""
            if cell.font and cell.font.color and isinstance(cell.font.color.rgb, str) and cell.font.color.rgb[-6:] == "FFFFFF":
                st += "color:#fff;font-weight:600;"
            if r == 1:
                st += "font:400 24px Georgia,serif;"
            if r == 5 and sheet not in ("Settings", "Start here"):
                st += "font-size:18px;font-weight:600;"
            cells.append(f'<td style="{st}">{fmt(v, cell.number_format or "")}</td>')
        out.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>" + "".join(out) + "</table>"


def chart_svg(wb, vals, w=900, h=360):
    ys = wb["Year"]
    n = min(2, ys.max_column - 1)
    series = []
    for k in range(n):
        series.append([float(vals.get(f"YEAR!{get_column_letter(2 + k)}{5 + m}", 0) or 0) for m in range(12)])
    top = max([max(s) for s in series] + [1])
    bw = (w - 80) / 12
    parts = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#fff"/>']
    for m in range(12):
        for k, s in enumerate(series):
            bh = (h - 70) * s[m] / top
            x = 50 + m * bw + k * (bw / (n + 1))
            parts.append(f'<rect x="{x:.1f}" y="{h - 40 - bh:.1f}" width="{bw / (n + 1) - 4:.1f}" height="{bh:.1f}" rx="4" fill="{PALETTE[k]}"/>')
        parts.append(f'<text x="{50 + m * bw + bw / 2 - 12:.1f}" y="{h - 16}" font-family="Inter,Segoe UI,Arial" font-size="13" fill="#8B7E6F">{ys.cell(row=5 + m, column=1).value}</text>')
    for k in range(n):
        parts.append(f'<rect x="{60 + k * 180}" y="12" width="14" height="14" rx="3" fill="{PALETTE[k]}"/><text x="{80 + k * 180}" y="24" font-family="Inter,Segoe UI,Arial" font-size="14" fill="#1A1A1A">{html.escape(str(ys.cell(row=4, column=2 + k).value))}</text>')
    return "".join(parts) + "</svg>"


CSS = """body{margin:0;font-family:Inter,'Segoe UI',Arial,sans-serif;color:#1A1A1A}
table{border-collapse:collapse;font-size:13px;background:#fff}td{border-bottom:1px solid #EFE7DC;padding:5px 9px;white-space:nowrap;height:18px;max-width:220px;overflow:hidden}
.laptop{position:relative;width:1060px}.laptop .scr{background:#111;border-radius:22px 22px 0 0;padding:22px;height:600px;overflow:hidden}
.laptop .scr>div{background:#fff;height:100%;overflow:hidden;border-radius:6px}.laptop .base{height:26px;background:linear-gradient(#d9d9de,#b9b9c0);border-radius:0 0 28px 28px;margin:0 -40px}
.tablet{background:#111;border-radius:40px;padding:30px;width:640px;height:820px}.tablet>div{background:#fff;border-radius:10px;height:100%;overflow:hidden}
.phone{background:#111;border-radius:52px;padding:18px;width:360px;height:740px}.phone>div{background:#FFFBF5;border-radius:36px;height:100%;overflow:hidden;padding:28px 18px;box-sizing:border-box}
.lab{font:600 13px/1 ui-monospace,Consolas,monospace;letter-spacing:.14em;text-transform:uppercase}
h1{font:400 66px/1.02 Georgia,'Palatino Linotype',serif;margin:18px 0}.kpi{background:#fff;border-radius:16px;padding:14px 16px;margin-bottom:10px;box-shadow:0 2px 18px rgba(0,0,0,.06)}
.kpi b{display:block;font:600 26px Inter,Arial}.tabs{display:flex;gap:6px;flex-wrap:wrap}.tab{padding:7px 12px;border-radius:8px;background:#EFE7DC;font-size:13px}.tab.on{background:#fff;color:#E8833A;font-weight:700}"""


def page(body, bg):
    return f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body style='width:1600px;height:1200px;overflow:hidden;background:{bg}'>{body}</body></html>"


def art_bg(title, art_q=None):
    """Public-domain painting for the cover (same source as the book covers); None if offline."""
    try:
        sys.path.insert(0, str(K.parents[1] / "sach" / "KHUNG"))
        import bia_sach
        words = [w for w in title.split() if len(w) > 3 and not w.isdigit()][:2]
        img, credit, oid = bia_sach.find_art(([art_q] if art_q else []) + words + ["still life", "landscape", "garden"])
        if img is None:
            return None, None
        img = bia_sach.cover_fill(img, 1600, 1200)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), {"credit": credit, "object": oid}
    except Exception as e:
        print("art", type(e).__name__, e)
        return None, None


def render(path, out, title, tagline, art_q=None):
    from playwright.sync_api import sync_playwright
    wb = load_workbook(path)
    vals = compute(path)
    jan, year, settings = table(wb, vals, "Jan", 30, 6), table(wb, vals, "Year", 18, 5), table(wb, vals, "Settings", 22, 3)
    kpis = "".join(f"<div class='kpi'><span class='lab' style='color:#8B7E6F'>{html.escape(str(wb['Jan'].cell(row=4, column=c).value or ''))}</span><b>{fmt(vals.get(f'JAN!{get_column_letter(c)}5'), wb['Jan'].cell(row=5, column=c).number_format)}</b></div>"
                   for c in range(1, 5) if wb["Jan"].cell(row=4, column=c).value)
    art, credit = art_bg(title, art_q)
    cover_bg = f"url({art}) center/cover" if art else "linear-gradient(135deg,#2B4A3B,#E8833A)"
    pages = {
        "cover-1600x1200.png": page(f"""<div style='position:absolute;inset:0;background:{cover_bg}'></div>
            <div style='position:absolute;left:0;top:0;bottom:0;width:640px;background:rgba(20,28,24,.82);color:#fff;padding:120px 64px;box-sizing:border-box'>
            <div class='lab' style='color:#E0A458'>Snoutsmith Templates · Google Sheets + Excel</div><h1>{html.escape(title)}</h1>
            <div style='font-size:22px;color:#E9E2D6'>{html.escape(tagline)}</div>
            <div style='margin-top:36px;display:inline-block;background:{ACCENT};border-radius:999px;padding:16px 30px;font-weight:700'>15 tabs · 12 months · charts</div></div>
            <div style='position:absolute;left:700px;top:250px;transform:scale(.82);transform-origin:top left'><div class='laptop'><div class='scr'><div><div style='zoom:1.55'>{year}</div></div></div><div class='base'></div></div></div>""", "#222"),
        "anh-2-thang-laptop.png": page(f"<div style='padding:90px 0 0 110px'><div class='lab' style='color:#fff'>Every month, the same clean layout</div><div style='height:30px'></div><div style='transform:scale(1.25);transform-origin:top left'><div class='laptop'><div class='scr'><div>{jan}</div></div><div class='base'></div></div></div></div>", "linear-gradient(135deg,#4F7CAC,#2B4A3B)"),
        "anh-3-nam-bieu-do.png": page(f"<div style='padding:70px 90px;display:grid;grid-template-columns:560px 1fr;gap:40px'><div><div class='lab' style='color:#8B7E6F'>The year fills itself</div><h1 style='font-size:52px'>{html.escape(title)}</h1><div style='background:#fff;border-radius:16px;padding:18px;box-shadow:0 2px 24px rgba(0,0,0,.08)'>{year}</div></div><div style='padding-top:120px'><div style='background:#fff;border-radius:16px;padding:22px;box-shadow:0 2px 24px rgba(0,0,0,.08)'>{chart_svg(wb, vals)}</div></div></div>", "#FFF4EA"),
        "anh-4-cai-dat-tablet.png": page(f"<div style='display:flex;gap:80px;padding:150px 120px'><div class='tablet'><div>{settings}</div></div><div style='padding-top:120px;color:#fff'><div class='lab' style='color:#FFE3C7'>Set up once</div><h1>Your categories,<br>your lists</h1><div style='font-size:22px'>Every month tab picks from these lists – no typing twice.</div></div></div>", "linear-gradient(135deg,#C8553D,#E0A458)"),
        "anh-5-dien-thoai.png": page(f"<div style='display:flex;gap:90px;padding:180px 160px'><div class='phone'><div><div class='lab' style='color:#E8833A'>January</div><div style='height:12px'></div>{kpis}<div style='transform:scale(.62);transform-origin:top left;width:520px'>{table(wb, vals, 'Jan', 14, 4, 7)}</div></div></div><div style='padding-top:160px;color:#fff'><div class='lab' style='color:#F2D7EE'>Works on your phone</div><h1>Check the month<br>anywhere</h1><div style='font-size:22px'>Google Sheets and Excel apps, free plans.</div></div></div>", "linear-gradient(135deg,#8E6C8A,#4F7CAC)"),
        "anh-6-ben-trong.png": page("<div style='padding:110px 120px'><div class='lab' style='color:#8B7E6F'>What's inside</div><h1>15 tabs, ready to use</h1><div style='display:grid;grid-template-columns:repeat(5,1fr);gap:18px;margin-top:40px'>"
                                     + "".join(f"<div style='background:{PALETTE[i % 6]};color:#fff;border-radius:16px;padding:26px 18px;font:600 22px Inter,Arial'>{html.escape(n)}</div>" for i, n in enumerate(wb.sheetnames))
                                     + "</div></div>", "#FFFBF5"),
    }
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 1600, "height": 1200})
        for name, html_ in pages.items():
            p.set_content(html_)
            p.wait_for_timeout(250)
            p.screenshot(path=str(out / name))
        b.close()
    from PIL import Image
    frames = [Image.open(out / n).convert("RGB").resize((800, 600)) for n in ("anh-2-thang-laptop.png", "anh-3-nam-bieu-do.png", "anh-4-cai-dat-tablet.png", "anh-5-dien-thoai.png")]
    frames[0].save(out / "demo.gif", save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    if credit:
        (out / "COVER-CREDIT.json").write_text(json.dumps(credit, ensure_ascii=False), encoding="utf-8")
    return {"images": len(pages), "gif": True, "art": bool(art)}


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]))
