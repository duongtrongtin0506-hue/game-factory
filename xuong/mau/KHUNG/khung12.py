"""Khung 12 tháng – chép cấu trúc 3 mẫu Etsy bán chạy ("budget planner google sheets", HỌC 21/10):

CHECKLIST CẤU TRÚC (≤ 15 dòng, chép cách làm, không chép chữ/hình):
 1. Tab "Start here": các bước dùng, mẹo, nơi gõ
 2. Tab "Settings": danh mục/tài khoản/thói quen… (≤ 20 dòng), tham số chung
 3. 12 tab tháng Jan…Dec, cùng một bố cục
 4. Đầu mỗi tháng: thẻ số tổng (KPI) tự tính
 5. Thân tháng: bảng nhập có danh sách thả xuống lấy từ Settings
 6. Ô nhập tô màu, ô công thức chữ xám – khó làm hỏng
 7. Tab "Year": mỗi tháng 1 dòng, kéo số từ 12 tab tháng, có tổng năm
 8. Biểu đồ năm (cột/đường) ngay trên tab Year
 9. Dữ liệu mẫu sẵn để thấy cách chạy; hướng dẫn xóa
10. Chạy trên Google Sheets + Excel gói miễn phí, không script
11. Bản nhân: đổi chủ đề = đổi danh mục, cột, thẻ số (cùng khung)

python KHUNG/khung12.py <slug> <out-dir>   → <slug>.xlsx
"""
import calendar
import datetime
import random
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mau import ACCENT, CALC, FILL_IN, HEAD, LABEL, MONEY, PCT, header, put, sheet_base, start_here  # noqa: E402

YEAR = 2026
MONTHS = [calendar.month_abbr[m] for m in range(1, 13)]
ROWS = 60          # input rows per month
FIRST = 8          # first input row on a month tab
LAST = FIRST + ROWS - 1
KPI_FILL = PatternFill("solid", fgColor="FFF4EA")


def _months_tabs(wb, spec, rnd):
    cols = spec["cols"]
    for mi, mname in enumerate(MONTHS):
        ws = wb.create_sheet(mname)
        sheet_base(ws, f"{calendar.month_name[mi + 1]} {YEAR}", spec["month_sub"], [c[2] for c in cols] + [4, 4])
        for k, (lab, f, fmt, _) in enumerate(spec["kpis"]):
            c = ws.cell(row=4, column=1 + k, value=lab.upper())
            c.font, c.fill = LABEL, KPI_FILL
            v = ws.cell(row=5, column=1 + k, value="=" + f.format(a=FIRST, b=LAST))
            v.font, v.fill, v.number_format = Font(size=16, color="1A1A1A"), KPI_FILL, fmt
        header(ws, FIRST - 1, [c[0] for c in cols])
        for ci, (name, kind, w, src) in enumerate(cols, 1):
            L = get_column_letter(ci)
            if kind == "list":
                dv = DataValidation(type="list", formula1=src, allow_blank=True)
                ws.add_data_validation(dv)
                dv.add(f"{L}{FIRST}:{L}{LAST}")
        rows = spec["sample"](mi, rnd)
        for r in range(ROWS):
            vals = rows[r] if r < len(rows) else [None] * len(cols)
            for ci, (name, kind, w, src) in enumerate(cols, 1):
                v = vals[ci - 1]
                if kind == "date" and v is None and r < len(rows):
                    v = datetime.date(YEAR, mi + 1, 1)
                put(ws, FIRST + r, ci, v, {"money": MONEY, "date": "yyyy-mm-dd", "pct": PCT}.get(kind), inp=True)
        for k, (lab, f, fmt, _) in enumerate(spec["kpis"]):
            if fmt == PCT:
                ws.conditional_formatting.add(f"{get_column_letter(1 + k)}5", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=ACCENT))


def _habit_tabs(wb, spec, rnd):
    habits = spec["settings_list"][1]
    for mi, mname in enumerate(MONTHS):
        days = calendar.monthrange(YEAR, mi + 1)[1]
        ws = wb.create_sheet(mname)
        sheet_base(ws, f"{calendar.month_name[mi + 1]} {YEAR}", "Type 1 on each day you did the habit", [22] + [3.2] * days + [8, 8])
        ws.cell(row=4, column=1, value="DONE THIS MONTH").font = LABEL
        last_col = get_column_letter(1 + days)
        v = ws.cell(row=5, column=1, value=f"=IF(COUNTA(A{FIRST}:A{FIRST + 11})=0,0,COUNT(B{FIRST}:{last_col}{FIRST + 11})/(COUNTA(A{FIRST}:A{FIRST + 11})*{days}))")
        v.font, v.number_format = Font(size=16), PCT
        header(ws, FIRST - 1, ["Habit"] + [str(d) for d in range(1, days + 1)] + ["Done", "%"])
        for i in range(12):
            r = FIRST + i
            c = ws.cell(row=r, column=1, value=f'=IF(Settings!A{6 + i}="","",Settings!A{6 + i})')
            c.font = CALC
            rate = 0.4 + rnd.random() * 0.5
            for d in range(days):
                cell = ws.cell(row=r, column=2 + d, value=1 if (i < len(habits) and mi < 10 and rnd.random() < rate) else None)
                cell.fill, cell.alignment = FILL_IN, Alignment(horizontal="center")
            put(ws, r, 2 + days, f"=COUNT(B{r}:{last_col}{r})")
            put(ws, r, 3 + days, f'=IF(A{r}="","",COUNT(B{r}:{last_col}{r})/{days})', PCT)
        ws.conditional_formatting.add(f"B{FIRST}:{last_col}{FIRST + 11}", CellIsRule(operator="equal", formula=["1"], fill=PatternFill("solid", fgColor=ACCENT), font=Font(color="FFFFFF")))


def _year(wb, spec):
    ys = wb.create_sheet("Year", 2)
    kpis = spec["kpis"] if spec["kind"] == "list" else [("Done", "", PCT, "avg")]
    sheet_base(ys, f"{YEAR} at a glance", "Pulled from the 12 month tabs – nothing to type here", [10] + [16] * len(kpis))
    header(ys, 4, ["Month"] + [k[0] for k in kpis])
    for mi, mname in enumerate(MONTHS):
        r = 5 + mi
        put(ys, r, 1, mname)
        for k, (lab, f, fmt, agg) in enumerate(kpis):
            put(ys, r, 2 + k, f"='{mname}'!{get_column_letter(1 + k)}5", fmt)
    put(ys, 17, 1, "Year")
    for k, (lab, f, fmt, agg) in enumerate(kpis):
        L = get_column_letter(2 + k)
        func = {"sum": "SUM", "avg": "AVERAGE", "last": "LOOKUP"}[agg]
        put(ys, 17, 2 + k, f"=SUM({L}5:{L}16)" if func == "SUM" else f"=AVERAGE({L}5:{L}16)" if func == "AVERAGE" else f"=IFERROR(INDEX({L}1:{L}16,SUMPRODUCT(MAX(({L}5:{L}16<>0)*ROW({L}5:{L}16)))),0)", fmt)   # last month with a number
    ch = (LineChart if spec.get("chart") == "line" else BarChart)()
    ch.title = spec["chart_title"]
    n = min(len(kpis), spec.get("chart_series", 2))
    ch.add_data(Reference(ys, min_col=2, max_col=1 + n, min_row=4, max_row=16), titles_from_data=True)
    ch.set_categories(Reference(ys, min_col=1, min_row=5, max_row=16))
    ch.height, ch.width = 8, 16
    ys.add_chart(ch, "A20")


def _settings(wb, spec):
    st = wb.create_sheet("Settings", 1)
    (title_a, items_a), extra = spec["settings_list"], spec.get("settings_extra")
    sheet_base(st, "Settings", "Edit these lists – every month tab uses them", [26, 14, 26, 14])
    header(st, 5, [title_a, spec.get("settings_list_b_title", "")] + ([extra[0]] if extra else []))
    st.freeze_panes = None
    for i in range(20):
        it = items_a[i] if i < len(items_a) else None
        put(st, 6 + i, 1, it[0] if isinstance(it, tuple) else it, inp=True)
        if isinstance(it, tuple):
            put(st, 6 + i, 2, it[1], spec.get("settings_b_fmt"), inp=True)
    if extra:
        for i, v in enumerate(extra[1]):
            put(st, 6 + i, 3, v, inp=True)


def build(spec, path):
    rnd = random.Random(spec["seed"])
    wb = Workbook()
    start_here(wb, spec["title"], spec["what"], spec["steps"] + ["Open Year to see the whole year and the chart (it fills itself)."],
               spec["notes"] + ["Sample data is filled in for January–October so you can see how it works: select the tinted rows on each month and press Delete."])
    _settings(wb, spec)
    (_habit_tabs if spec["kind"] == "grid" else _months_tabs)(wb, spec, rnd)
    _year(wb, spec)
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = ACCENT if ws.title in ("Start here", "Year") else "E8E0D5"
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return {"sheets": wb.sheetnames, "months": 12}


# ------------------------------------------------------------------ 8 specs (nhân bản: đổi danh mục, cột, thẻ số)
def _rng_rows(mi, rnd, n, make):
    if mi >= 10:
        return []
    return [make(mi, rnd, i) for i in range(n)]


CATS = [("Salary", "Income"), ("Side income", "Income"), ("Rent", "Expense"), ("Groceries", "Expense"), ("Utilities", "Expense"), ("Transport", "Expense"),
        ("Dining out", "Expense"), ("Shopping", "Expense"), ("Health", "Expense"), ("Fun", "Expense"), ("Savings", "Savings"), ("Debt payment", "Savings")]
SPECS = {
    "budget-planner": dict(
        title="Budget Planner 2026", tagline="12 months, a year dashboard and charts", seed=1, kind="list",
        what="Plan and track every month of 2026: log income and spending, see income, expenses, savings and what is left, and watch the year build up on one dashboard.",
        steps=["List your categories on Settings (Income, Expense or Savings).", "Log each transaction on its month tab: date, category, type, amount."],
        notes=["Type is picked from the list – Income, Expense or Savings.", "Totals and charts update by themselves."],
        settings_list=("Category", CATS), settings_list_b_title="Type", month_sub="One line per transaction",
        cols=[("Date", "date", 13, None), ("Category", "list", 20, "=Settings!$A$6:$A$25"), ("Type", "list", 12, '"Income,Expense,Savings"'), ("Amount", "money", 13, None), ("Note", "text", 28, None)],
        kpis=[("Income", 'SUMIFS(D{a}:D{b},C{a}:C{b},"Income")', MONEY, "sum"), ("Expenses", 'SUMIFS(D{a}:D{b},C{a}:C{b},"Expense")', MONEY, "sum"),
              ("Saved", 'SUMIFS(D{a}:D{b},C{a}:C{b},"Savings")', MONEY, "sum"), ("Left", 'SUMIFS(D{a}:D{b},C{a}:C{b},"Income")-SUMIFS(D{a}:D{b},C{a}:C{b},"<>Income")', MONEY, "sum")],
        chart_title="Income vs expenses", chart_series=2,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 16, lambda mi, rnd, i: (lambda c: [datetime.date(YEAR, mi + 1, 1 + i), c[0], c[1],
                                         round(rnd.uniform(3600, 4200) if c[0] == "Salary" else rnd.uniform(150, 600) if c[1] == "Income" else rnd.uniform(15, 400), 2), ""])(CATS[0] if i == 0 else CATS[1] if i == 1 else rnd.choice(CATS[2:])))),
    "debt-tracker": dict(
        title="Debt Payoff Tracker 2026", tagline="Log payments, watch balances fall month by month", seed=2, kind="list",
        what="Track every payment toward your debts for a year: principal, interest and what is left, month by month and on a year chart.",
        steps=["List each debt and its starting balance on Settings.", "Log payments on the month tab: debt, payment, interest charged."],
        notes=["Principal paid = payment − interest.", "Planning tool only, not financial advice."],
        settings_list=("Debt", [("Credit card", 4200), ("Car loan", 9800), ("Student loan", 15200), ("Store card", 900)]), settings_list_b_title="Start balance", settings_b_fmt=MONEY,
        month_sub="One line per payment",
        cols=[("Date", "date", 13, None), ("Debt", "list", 20, "=Settings!$A$6:$A$25"), ("Payment", "money", 13, None), ("Interest", "money", 13, None), ("Note", "text", 24, None)],
        kpis=[("Paid", "SUM(C{a}:C{b})", MONEY, "sum"), ("Interest", "SUM(D{a}:D{b})", MONEY, "sum"), ("Principal", "SUM(C{a}:C{b})-SUM(D{a}:D{b})", MONEY, "sum")],
        chart_title="Paid vs interest per month", chart_series=2,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 4, lambda mi, rnd, i: [datetime.date(YEAR, mi + 1, 5 + i * 5), ["Credit card", "Car loan", "Student loan", "Store card"][i],
                                                                     [250, 310, 180, 60][i], round([70, 55, 60, 18][i] * (1 - mi * 0.04), 2), ""])),
    "savings-goals": dict(
        title="Savings Goals Tracker 2026", tagline="Every deposit, every goal, the whole year", seed=3, kind="list",
        what="Save toward several goals at once: log deposits each month and see how much went to savings every month of the year.",
        steps=["List your goals and targets on Settings.", "Log each deposit on its month tab."],
        notes=["Withdrawals: type a negative amount.", "Targets live on Settings, column B."],
        settings_list=("Goal", [("Emergency fund", 10000), ("Vacation", 3000), ("New laptop", 1800), ("Car", 6000), ("Gifts", 800)]), settings_list_b_title="Target", settings_b_fmt=MONEY,
        month_sub="One line per deposit",
        cols=[("Date", "date", 13, None), ("Goal", "list", 20, "=Settings!$A$6:$A$25"), ("Amount", "money", 13, None), ("Note", "text", 28, None)],
        kpis=[("Saved", "SUM(C{a}:C{b})", MONEY, "sum"), ("Deposits", "COUNT(C{a}:C{b})", "0", "sum"), ("Biggest", "MAX(C{a}:C{b})", MONEY, "avg")],
        chart_title="Saved per month", chart_series=1,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 6, lambda mi, rnd, i: [datetime.date(YEAR, mi + 1, 2 + i * 4), ["Emergency fund", "Vacation", "New laptop", "Car", "Gifts", "Emergency fund"][i], rnd.choice([50, 75, 100, 150, 200]), ""])),
    "habit-tracker": dict(
        title="Habit Tracker 2026", tagline="Twelve habits, every day of the year", seed=4, kind="grid",
        what="Tick up to 12 habits every day of 2026 and see your completion rate per month and for the year.",
        steps=["Write your habits on Settings.", "Type 1 under each day you did the habit."],
        notes=["Each month tab has the right number of days.", "Done % = ticks ÷ (habits × days)."],
        settings_list=("Habit", ["Walk 8,000 steps", "Read 20 pages", "Drink 2 L water", "Sleep by 11 pm", "Stretch 10 min", "Journal", "No sugar", "Practice a language"]),
        kpis=[("Done", "", PCT, "avg")], chart_title="Done % per month", chart="line", sample=None, month_sub=""),
    "weekly-planner": dict(
        title="Weekly Planner 2026", tagline="Tasks, priorities and done-rates for every month", seed=5, kind="list",
        what="Plan the weeks of each month: tasks with day, priority and a done tick, with done-rates per month and for the year.",
        steps=["Adjust the priority list on Settings if you like.", "Add tasks on the month tab: date, task, priority; type x when done."],
        notes=["Sort a month by date or priority with the filter button.", "The year chart shows planned vs done."],
        settings_list=("Priority", ["High", "Medium", "Low"]), month_sub="One line per task",
        cols=[("Date", "date", 13, None), ("Task", "text", 30, None), ("Priority", "list", 12, "=Settings!$A$6:$A$25"), ("Done", "list", 8, '"x"')],
        kpis=[("Tasks", "COUNTA(B{a}:B{b})", "0", "sum"), ("Done", 'COUNTIF(D{a}:D{b},"x")', "0", "sum"), ("Done %", 'IF(COUNTA(B{a}:B{b})=0,0,COUNTIF(D{a}:D{b},"x")/COUNTA(B{a}:B{b}))', PCT, "avg")],
        chart_title="Tasks planned vs done", chart_series=2,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 14, lambda mi, rnd, i: [datetime.date(YEAR, mi + 1, 1 + i * 2), rnd.choice(["Pay bills", "Gym", "Call family", "Plan meals", "Clean desk", "Read", "Project work", "Groceries", "Car service", "Budget review"]),
                                                                      rnd.choice(["High", "Medium", "Low"]), "x" if rnd.random() < 0.75 else None])),
    "meal-planner": dict(
        title="Meal Planner 2026", tagline="Meals and food cost for every month", seed=6, kind="list",
        what="Plan meals for each month, note the cost, and see meals planned, money spent and eating-out share across the year.",
        steps=["Edit meal types on Settings.", "Add meals on the month tab: date, meal type, dish, cost, where."],
        notes=["'Where' is Home or Out – the year view shows the share eaten out.", "Use the Note column for the shopping list."],
        settings_list=("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"]), month_sub="One line per meal",
        cols=[("Date", "date", 13, None), ("Meal", "list", 12, "=Settings!$A$6:$A$25"), ("Dish", "text", 26, None), ("Cost", "money", 11, None), ("Where", "list", 9, '"Home,Out"')],
        kpis=[("Meals", "COUNTA(C{a}:C{b})", "0", "sum"), ("Food cost", "SUM(D{a}:D{b})", MONEY, "sum"), ("Eaten out", 'IF(COUNTA(C{a}:C{b})=0,0,COUNTIF(E{a}:E{b},"Out")/COUNTA(C{a}:C{b}))', PCT, "avg")],
        chart_title="Meals and food cost", chart_series=2,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 30, lambda mi, rnd, i: (lambda out: [datetime.date(YEAR, mi + 1, 1 + i % 28), ["Breakfast", "Lunch", "Dinner"][i % 3],
                                         rnd.choice(["Oats", "Chicken wrap", "Pasta", "Stir-fry", "Salad", "Tacos", "Soup", "Pizza", "Curry", "Eggs"]), round(rnd.uniform(9, 24) if out else rnd.uniform(2, 7), 2), "Out" if out else "Home"])(rnd.random() < 0.2))),
    "net-worth": dict(
        title="Net Worth Tracker 2026", tagline="Assets, debts and net worth, month by month", seed=7, kind="list",
        what="Record your account balances once a month and watch assets, liabilities and net worth move across the year on a line chart.",
        steps=["List your accounts on Settings.", "Once a month, copy each balance onto the month tab and pick Asset or Liability."],
        notes=["Liabilities are typed as positive numbers – the sheet subtracts them.", "Not financial advice; a record-keeping tool."],
        settings_list=("Account", ["Checking", "Savings", "Brokerage", "Retirement", "Home value", "Mortgage", "Car loan", "Credit card"]), month_sub="One line per account balance",
        cols=[("Account", "list", 20, "=Settings!$A$6:$A$25"), ("Type", "list", 12, '"Asset,Liability"'), ("Balance", "money", 15, None), ("Note", "text", 26, None)],
        kpis=[("Assets", 'SUMIFS(C{a}:C{b},B{a}:B{b},"Asset")', MONEY, "last"), ("Liabilities", 'SUMIFS(C{a}:C{b},B{a}:B{b},"Liability")', MONEY, "last"),
              ("Net worth", 'SUMIFS(C{a}:C{b},B{a}:B{b},"Asset")-SUMIFS(C{a}:C{b},B{a}:B{b},"Liability")', MONEY, "last")],
        chart_title="Net worth over the year", chart="line", chart_series=3,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 8, lambda mi, rnd, i: [["Checking", "Savings", "Brokerage", "Retirement", "Home value", "Mortgage", "Car loan", "Credit card"][i],
                                                                     "Asset" if i < 5 else "Liability", round([3200, 9000, 21000, 48000, 310000, 240000, 9800, 1600][i] * (1 + (0.01 if i < 5 else -0.012) * mi), 2), ""])),
    "subscription-tracker": dict(
        title="Subscription Tracker 2026", tagline="Every subscription charge, every month", seed=8, kind="list",
        what="List your subscriptions once, log each charge as it happens, and see monthly and yearly subscription spend with a chart.",
        steps=["List subscriptions and their usual price on Settings.", "Log each charge on its month tab."],
        notes=["Mark Keep or Cancel in the Decision column when you review.", "Year total shows what subscriptions cost you in 2026."],
        settings_list=("Subscription", [("Streaming", 15.49), ("Music", 10.99), ("Cloud storage", 2.99), ("Gym", 39), ("News", 8), ("Phone plan", 35), ("Software", 12)]),
        settings_list_b_title="Usual price", settings_b_fmt=MONEY, month_sub="One line per charge",
        cols=[("Date", "date", 13, None), ("Subscription", "list", 20, "=Settings!$A$6:$A$25"), ("Charged", "money", 12, None), ("Decision", "list", 10, '"Keep,Cancel"')],
        kpis=[("Spent", "SUM(C{a}:C{b})", MONEY, "sum"), ("Charges", "COUNT(C{a}:C{b})", "0", "sum"), ("To cancel", 'COUNTIF(D{a}:D{b},"Cancel")', "0", "sum")],
        chart_title="Subscription spend per month", chart_series=1,
        sample=lambda mi, rnd: _rng_rows(mi, rnd, 7, lambda mi, rnd, i: [datetime.date(YEAR, mi + 1, 3 + i * 3), ["Streaming", "Music", "Cloud storage", "Gym", "News", "Phone plan", "Software"][i],
                                                                     [15.49, 10.99, 2.99, 39, 8, 35, 12][i], "Cancel" if (i == 4 and mi > 6) else "Keep"])),
}

if __name__ == "__main__":
    s = sys.argv[1]
    print(build(SPECS[s], Path(sys.argv[2]) / f"{s}.xlsx"))
