"""Self-made spreadsheet templates (Excel .xlsx that opens in Google Sheets and Excel, free plans) for
templates.snoutsmith.com. python KHUNG/mau.py <slug|all> [--out HANG]

Every template: a "Start here" sheet, sample data, formulas only (no macros, no scripts, no add-ons), one accent
colour (#E8833A, templates shop), frozen headers, input cells tinted, formula cells locked-looking (grey text).
Fonts: none embedded (the app's default font). Writes per template: <slug>.xlsx, preview PNG 1600x1200 rendered from
the computed values, BAN-GIAO.md, LICENSES.md, STORE.md, meta.json. Formula check: KHUNG/kiem_cong_thuc.py.
"""
import datetime
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

K = Path(__file__).resolve().parent
ROOT = K.parent
ACCENT = "E8833A"
INK, SOFT, LINE, PAPER, INPUT = "1A1A1A", "8B7E6F", "E8E0D5", "FFFBF5", "FFF4EA"
H1 = Font(size=20, bold=False, color=INK)
LABEL = Font(size=9, bold=True, color=SOFT)
HEAD = Font(size=10, bold=True, color="FFFFFF")
BODY = Font(size=10, color=INK)
CALC = Font(size=10, color="555555")
THIN = Border(bottom=Side(style="thin", color=LINE))
FILL_HEAD = PatternFill("solid", fgColor=ACCENT)
FILL_IN = PatternFill("solid", fgColor=INPUT)
FILL_PAPER = PatternFill("solid", fgColor=PAPER)
MONEY = '"$"#,##0.00'
PCT = "0%"


def sheet_base(ws, title, subtitle, widths):
    ws.sheet_view.showGridLines = False
    ws["A1"] = title
    ws["A1"].font = H1
    ws["A2"] = subtitle
    ws["A2"].font = Font(size=10, color=SOFT)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 30


def header(ws, row, names):
    for i, n in enumerate(names, 1):
        c = ws.cell(row=row, column=i, value=n)
        c.font, c.fill, c.alignment = HEAD, FILL_HEAD, Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 22
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def put(ws, row, col, value, fmt=None, inp=False):
    c = ws.cell(row=row, column=col, value=value)
    c.font = CALC if isinstance(value, str) and value.startswith("=") else BODY
    c.border = THIN
    if fmt:
        c.number_format = fmt
    if inp:
        c.fill = FILL_IN
    return c


def start_here(wb, name, what, steps, notes):
    ws = wb.active
    ws.title = "Start here"
    sheet_base(ws, name, "Free template · templates.snoutsmith.com", [4, 90])
    r = 4
    ws.cell(row=r, column=2, value="WHAT IT DOES").font = LABEL
    ws.cell(row=r + 1, column=2, value=what).alignment = Alignment(wrap_text=True)
    ws.row_dimensions[r + 1].height = 34
    r += 3
    ws.cell(row=r, column=2, value="HOW TO USE").font = LABEL
    for i, s in enumerate(steps, 1):
        ws.cell(row=r + i, column=2, value=f"{i}. {s}").alignment = Alignment(wrap_text=True)
    r += len(steps) + 2
    ws.cell(row=r, column=2, value="GOOD TO KNOW").font = LABEL
    for i, s in enumerate(notes, 1):
        ws.cell(row=r + i, column=2, value="• " + s).alignment = Alignment(wrap_text=True)
    r += len(notes) + 2
    ws.cell(row=r, column=2, value="Tinted cells are yours to type in. Grey numbers are formulas – leave them. Works in Google Sheets (File → Import or open the .xlsx) and Excel, free plans, no add-ons or scripts.").font = Font(size=9, color=SOFT)
    ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True)
    return ws


# ------------------------------------------------------------------ templates
def monthly_budget(wb):
    start_here(wb, "Monthly Budget (50/30/20)", "Plan a month of income and spending, see actual vs planned per category and how close you are to the 50/30/20 split.",
               ["Type your monthly take-home income on the Budget sheet.", "Adjust the planned amount for each category (or keep the examples).",
                "Log spending on the Spending sheet: date, category, amount.", "Budget shows actual, left to spend and your needs/wants/savings split."],
               ["Categories are tagged Need, Want or Savings – change the tag in column B.", "Delete the sample rows on Spending (rows 5–44) to start fresh."])
    sp = wb.create_sheet("Spending")
    sheet_base(sp, "Spending log", "One line per purchase", [14, 22, 14, 36])
    header(sp, 4, ["Date", "Category", "Amount", "Note"])
    cats = [("Rent / mortgage", "Need", 1400), ("Utilities", "Need", 180), ("Groceries", "Need", 450), ("Transport", "Need", 220), ("Insurance", "Need", 160),
            ("Phone & internet", "Need", 90), ("Dining out", "Want", 200), ("Entertainment", "Want", 120), ("Shopping", "Want", 150), ("Subscriptions", "Want", 45),
            ("Travel fund", "Want", 150), ("Emergency fund", "Savings", 400), ("Retirement", "Savings", 350), ("Extra debt payment", "Savings", 150)]
    import random
    rnd = random.Random(7)
    for i in range(40):
        c = rnd.choice(cats[:11])
        put(sp, 5 + i, 1, datetime.date(2026, 10, 1 + i % 28), "yyyy-mm-dd", True)
        put(sp, 5 + i, 2, c[0], inp=True)
        put(sp, 5 + i, 3, round(c[2] / rnd.randint(4, 9), 2), MONEY, True)
        put(sp, 5 + i, 4, "sample", inp=True)
    dv = DataValidation(type="list", formula1="=Budget!$A$7:$A$20", allow_blank=True)
    sp.add_data_validation(dv)
    dv.add("B5:B500")
    b = wb.create_sheet("Budget", 1)
    sheet_base(b, "Budget", "October 2026 – change the month name freely", [24, 10, 14, 14, 14, 12])
    b["A4"], b["B4"] = "Monthly income", 4200
    b["A4"].font = LABEL
    b["B4"].fill, b["B4"].number_format = FILL_IN, MONEY
    header(b, 6, ["Category", "Type", "Planned", "Actual", "Left", "% used"])
    for i, (n, t, p) in enumerate(cats):
        r = 7 + i
        put(b, r, 1, n, inp=True)
        put(b, r, 2, t, inp=True)
        put(b, r, 3, p, MONEY, True)
        put(b, r, 4, f"=SUMIFS(Spending!$C$5:$C$500,Spending!$B$5:$B$500,A{r})", MONEY)
        put(b, r, 5, f"=C{r}-D{r}", MONEY)
        put(b, r, 6, f"=IF(C{r}=0,0,D{r}/C{r})", PCT)
    tv = DataValidation(type="list", formula1='"Need,Want,Savings"', allow_blank=False)
    b.add_data_validation(tv)
    tv.add("B7:B20")
    b.conditional_formatting.add("E7:E20", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C0392B")))
    b.conditional_formatting.add("F7:F20", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=ACCENT))
    put(b, 21, 1, "Total")
    for col in (3, 4, 5):
        L = get_column_letter(col)
        put(b, 21, col, f"=SUM({L}7:{L}20)", MONEY)
    b["A23"] = "SPLIT (target 50 / 30 / 20)"
    b["A23"].font = LABEL
    header_row = 24
    for i, n in enumerate(["Type", "Planned", "% of income", "Target"], 1):
        c = b.cell(row=header_row, column=i, value=n)
        c.font, c.fill = HEAD, FILL_HEAD
    for i, (t, tgt) in enumerate([("Need", 0.5), ("Want", 0.3), ("Savings", 0.2)]):
        r = 25 + i
        put(b, r, 1, t)
        put(b, r, 2, f"=SUMIFS($C$7:$C$20,$B$7:$B$20,A{r})", MONEY)
        put(b, r, 3, f"=IF($B$4=0,0,B{r}/$B$4)", PCT)
        put(b, r, 4, tgt, PCT)
    put(b, 28, 1, "Unplanned income")
    put(b, 28, 2, "=B4-C21", MONEY)
    ch = PieChart()
    ch.title = "Planned split"
    ch.add_data(Reference(b, min_col=2, min_row=24, max_row=27), titles_from_data=True)
    ch.set_categories(Reference(b, min_col=1, min_row=25, max_row=27))
    ch.height, ch.width = 7, 9
    b.add_chart(ch, "H6")
    return {"sheets": ["Start here", "Budget", "Spending"], "sample_rows": 40, "checks": [("Budget", "C21"), ("Budget", "D21"), ("Budget", "C25")]}


def habit_tracker(wb):
    start_here(wb, "Habit Tracker", "Track up to 12 daily habits for a month: tick each day, see your % done and current streak per habit.",
               ["On Habits, write your habits in column A (examples given).", "Type 1 on each day you did the habit (blank = not done).", "Columns AH–AJ show days done, % and the streak up to the last ticked day."],
               ["Change the month in cell B2; days 29–31 simply stay blank in shorter months.", "Clear the sample ticks by selecting C5:AG16 and pressing Delete."])
    ws = wb.create_sheet("Habits")
    sheet_base(ws, "Habits", "October 2026", [22, 6] + [3.2] * 31 + [9, 8, 9])
    header(ws, 4, ["Habit", "Goal"] + [str(d) for d in range(1, 32)] + ["Done", "%", "Streak"])
    habits = ["Walk 8,000 steps", "Read 20 pages", "No sugar", "Drink 2 L water", "Sleep by 11 pm", "Stretch 10 min", "Journal", "Practice language",
              "No phone after 10 pm", "Cook at home", "Save $10", "Call family"]
    import random
    rnd = random.Random(3)
    for i, h in enumerate(habits):
        r = 5 + i
        put(ws, r, 1, h, inp=True)
        put(ws, r, 2, 25, inp=True)
        rate = 0.45 + rnd.random() * 0.45
        for d in range(31):
            c = ws.cell(row=r, column=3 + d, value=1 if (d < 21 and rnd.random() < rate) else None)
            c.fill, c.alignment, c.border = FILL_IN, Alignment(horizontal="center"), THIN
        put(ws, r, 34, f"=COUNT(C{r}:AG{r})")
        put(ws, r, 35, f"=IF(B{r}=0,0,AH{r}/B{r})", PCT)
        # streak: consecutive ticks ending at the last ticked day of the row
        put(ws, r, 36, f"=IF(AH{r}=0,0,{streak_formula(r)})")
        streak_helpers(ws, r)
    ws.conditional_formatting.add("C5:AG16", CellIsRule(operator="equal", formula=["1"], fill=PatternFill("solid", fgColor=ACCENT), font=Font(color="FFFFFF")))
    ws.conditional_formatting.add("AI5:AI16", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=ACCENT))
    return {"sheets": ["Start here", "Habits"], "sample_rows": 12, "checks": [("Habits", "AH5"), ("Habits", "AI5"), ("Habits", "AJ5")]}


def streak_formula(r):
    """Run length at the last ticked day. Helper columns AL:BP hold the running streak per day (hidden)."""
    cols = [get_column_letter(3 + d) for d in range(31)]
    last = "MAX(" + ",".join(f"IF({c}{r}=1,{i + 1},0)" for i, c in enumerate(cols)) + ")"
    return f"INDEX(AL{r}:BP{r},1,{last})"


def streak_helpers(ws, r):
    for d in range(31):
        col = 38 + d   # AL = 38
        day = get_column_letter(3 + d)
        prev = get_column_letter(col - 1)
        ws.cell(row=r, column=col, value=f"=IF({day}{r}=1,1,0)" if d == 0 else f"=IF({day}{r}=1,{prev}{r}+1,0)").font = CALC
        ws.column_dimensions[get_column_letter(col)].hidden = True

def weekly_planner(wb):
    start_here(wb, "Weekly Planner", "Plan one week on one page: top 3 priorities, a daily to-do list with done ticks, and an hour-by-hour plan.",
               ["Type the Monday date in C4 – the other dates fill in.", "Write your top 3 priorities and the to-dos for each day.", "Type x in Done when finished; the progress line counts them."],
               ["Duplicate the Week sheet (right-click → Duplicate) for the next week.", "Delete the sample text to start fresh."])
    ws = wb.create_sheet("Week")
    sheet_base(ws, "Week plan", "One page, seven days", [12] + [20, 5] * 7)
    ws["A4"], ws["C4"] = "Week of", datetime.date(2026, 10, 19)
    ws["A4"].font = LABEL
    ws["C4"].fill, ws["C4"].number_format = FILL_IN, "yyyy-mm-dd"
    ws["A6"] = "TOP 3"
    ws["A6"].font = LABEL
    for i, p in enumerate(["Finish the quarterly report", "Three workouts", "Plan the weekend trip"]):
        put(ws, 7 + i, 2, p, inp=True)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hr = 11
    for d, name in enumerate(days):
        col = 2 + d * 2
        c = ws.cell(row=hr, column=col, value=name)
        c.font, c.fill = HEAD, FILL_HEAD
        ws.cell(row=hr, column=col + 1).fill = FILL_HEAD
        put(ws, hr + 1, col, f"=$C$4+{d}", "ddd d mmm")
        sample = [["Team meeting 10:00", "Report draft", "Gym"], ["Report review", "Groceries"], ["Gym", "Call bank"], ["Send report", "Dentist 15:00"],
                  ["Gym", "Plan trip"], ["Market", "Hike"], ["Meal prep", "Read"]][d]
        for i in range(8):
            put(ws, hr + 2 + i, col, sample[i] if i < len(sample) else None, inp=True)
            put(ws, hr + 2 + i, col + 1, "x" if i < len(sample) - 1 else None, inp=True)
        put(ws, hr + 10, col, f'=COUNTIF({get_column_letter(col + 1)}{hr + 2}:{get_column_letter(col + 1)}{hr + 9},"x")&" / "&COUNTA({get_column_letter(col)}{hr + 2}:{get_column_letter(col)}{hr + 9})')
    ws.cell(row=hr + 10, column=1, value="Done").font = LABEL
    put(ws, hr + 12, 1, "Week")
    done = "+".join(f'COUNTIF({get_column_letter(3 + d * 2)}{hr + 2}:{get_column_letter(3 + d * 2)}{hr + 9},"x")' for d in range(7))
    tot = "+".join(f'COUNTA({get_column_letter(2 + d * 2)}{hr + 2}:{get_column_letter(2 + d * 2)}{hr + 9})' for d in range(7))
    put(ws, hr + 12, 2, f"=IF(({tot})=0,0,({done})/({tot}))", PCT)
    return {"sheets": ["Start here", "Week"], "sample_rows": 21, "checks": [("Week", "B23"), ("Week", "B12")]}


def savings_goals(wb):
    start_here(wb, "Savings Goals Tracker", "Track several savings goals: target, saved so far, monthly amount, % reached and the month you will hit each goal.",
               ["List your goals with a target amount and target date.", "Log every deposit on the Deposits sheet.", "Goals shows progress, what to save each month and the expected finish."],
               ["Expected finish assumes your average monthly deposit so far keeps going.", "Delete sample deposits (rows 5–36) to start fresh."])
    dp = wb.create_sheet("Deposits")
    sheet_base(dp, "Deposits", "One line per deposit", [14, 22, 14])
    header(dp, 4, ["Date", "Goal", "Amount"])
    goals = [("Emergency fund", 10000, datetime.date(2027, 12, 31)), ("Vacation", 3000, datetime.date(2027, 6, 30)), ("New laptop", 1800, datetime.date(2027, 3, 31)),
             ("Car down payment", 6000, datetime.date(2028, 6, 30)), ("Holiday gifts", 800, datetime.date(2026, 12, 15))]
    import random
    rnd = random.Random(11)
    for i in range(32):
        g = goals[i % 5]
        put(dp, 5 + i, 1, datetime.date(2026, 3 + i // 5, 1 + (i * 3) % 27), "yyyy-mm-dd", True)
        put(dp, 5 + i, 2, g[0], inp=True)
        put(dp, 5 + i, 3, rnd.choice([50, 75, 100, 150, 200, 250]), MONEY, True)
    g = wb.create_sheet("Goals", 1)
    sheet_base(g, "Goals", "Today's date drives the months left", [22, 13, 14, 13, 10, 12, 14, 16])
    g["A3"], g["B3"] = "Today", "=TODAY()"
    g["A3"].font, g["B3"].number_format = LABEL, "yyyy-mm-dd"
    header(g, 5, ["Goal", "Target", "Target date", "Saved", "% reached", "Months left", "Save per month", "Months to finish"])
    for i, (n, t, d) in enumerate(goals):
        r = 6 + i
        put(g, r, 1, n, inp=True)
        put(g, r, 2, t, MONEY, True)
        put(g, r, 3, d, "yyyy-mm-dd", True)
        put(g, r, 4, f"=SUMIFS(Deposits!$C$5:$C$500,Deposits!$B$5:$B$500,A{r})", MONEY)
        put(g, r, 5, f"=IF(B{r}=0,0,MIN(1,D{r}/B{r}))", PCT)
        put(g, r, 6, f"=MAX(0,ROUND((C{r}-$B$3)/30.44,0))")
        put(g, r, 7, f"=IF(F{r}=0,MAX(0,B{r}-D{r}),MAX(0,B{r}-D{r})/F{r})", MONEY)
        put(g, r, 8, f'=IF(D{r}>=B{r},0,IFERROR(ROUND((B{r}-D{r})/(D{r}/MAX(1,COUNTIFS(Deposits!$B$5:$B$500,A{r}))),0),"–"))')
    dv = DataValidation(type="list", formula1="=Goals!$A$6:$A$15", allow_blank=True)
    dp.add_data_validation(dv)
    dv.add("B5:B500")
    g.conditional_formatting.add("E6:E15", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=ACCENT))
    ch = BarChart()
    ch.type, ch.title = "bar", "Saved vs target"
    ch.add_data(Reference(g, min_col=2, min_row=5, max_row=10), titles_from_data=True)
    ch.add_data(Reference(g, min_col=4, min_row=5, max_row=10), titles_from_data=True)
    ch.set_categories(Reference(g, min_col=1, min_row=6, max_row=10))
    ch.height, ch.width = 7, 12
    g.add_chart(ch, "A13")
    return {"sheets": ["Start here", "Goals", "Deposits"], "sample_rows": 32, "checks": [("Goals", "D6"), ("Goals", "E6"), ("Goals", "G6")]}


def debt_snowball(wb):
    start_here(wb, "Debt Payoff Planner (Snowball / Avalanche)", "List up to 10 debts, pick snowball (smallest balance first) or avalanche (highest rate first), add an extra monthly amount, and see the payoff order, the month each debt is paid off and your debt-free date – simulated month by month.",
               ["Enter each debt on Plan: balance, yearly interest rate, minimum payment.", "Choose the method in B4, your extra monthly payment in B5 and the start month in B6.",
                "Plan shows the order, the month each debt is gone and the debt-free date. Schedule shows every month's balances."],
               ["The simulation pays every minimum, puts the extra (plus minimums freed by paid-off debts) on the debt in focus, and adds monthly interest.",
                "Estimates assume fixed rates and no new charges. A planning tool, not financial advice."])
    N, M = 10, 240
    ws = wb.create_sheet("Plan")
    sheet_base(ws, "Debt payoff plan", "Simulated month by month – estimates, not financial advice", [22, 14, 10, 13, 9, 16, 16])
    for r, (lab, val, f) in enumerate([("Method", "Snowball", None), ("Extra per month", 200, MONEY), ("Start month", datetime.date(2026, 11, 1), "mmm yyyy")], 4):
        ws.cell(row=r, column=1, value=lab).font = LABEL
        c = ws.cell(row=r, column=2, value=val)
        c.fill = FILL_IN
        if f:
            c.number_format = f
    mv = DataValidation(type="list", formula1='"Snowball,Avalanche"')
    ws.add_data_validation(mv)
    mv.add("B4")
    header(ws, 8, ["Debt", "Balance", "Rate / yr", "Min payment", "Order", "Paid off in month", "Paid off"])
    debts = [("Credit card A", 3200, 0.229, 95), ("Store card", 850, 0.269, 35), ("Car loan", 9400, 0.069, 260), ("Student loan", 14800, 0.049, 170),
             ("Personal loan", 4100, 0.119, 140), ("Credit card B", 1900, 0.199, 60)]
    for i in range(N):
        r = 9 + i
        n, bal, rate, mn = debts[i] if i < len(debts) else (None, None, None, None)
        put(ws, r, 1, n, inp=True)
        put(ws, r, 2, bal, MONEY, True)
        put(ws, r, 3, rate, "0.0%", True)
        put(ws, r, 4, mn, MONEY, True)
        put(ws, r, 5, f'=IF(N(B{r})=0,"",IF($B$4="Avalanche",COUNTIFS($B$9:$B$18,">0",$C$9:$C$18,">"&C{r})+COUNTIFS($B$9:$B$18,">0",$C$9:$C$18,C{r},$B$9:$B$18,"<"&B{r})+COUNTIFS($A$9:A{r},"<>",$B$9:B{r},B{r},$C$9:C{r},C{r}),'
                        f'COUNTIFS($B$9:$B$18,">0",$B$9:$B$18,"<"&B{r})+COUNTIFS($B$9:B{r},B{r})))')
        col = get_column_letter(2 + i)
        put(ws, r, 6, f'=IF(N(B{r})=0,"",IF(INDEX(Schedule!{col}$5:{col}${4 + M},{M})>0,"over {M // 12} years",COUNTIF(Schedule!{col}$5:{col}${4 + M},">0")+1))')
        put(ws, r, 7, f'=IF(ISNUMBER(F{r}),DATE(YEAR($B$6),MONTH($B$6)+F{r}-1,1),"")', "mmm yyyy")
    put(ws, 19, 1, "Total")
    put(ws, 19, 2, "=SUM(B9:B18)", MONEY)
    put(ws, 19, 4, "=SUM(D9:D18)", MONEY)
    ws.cell(row=21, column=1, value="DEBT-FREE").font = LABEL
    put(ws, 22, 1, "Month number")
    put(ws, 22, 2, '=IF(COUNT(F9:F18)<COUNT(B9:B18),"over 20 years",MAX(F9:F18))')
    put(ws, 23, 1, "Date")
    put(ws, 23, 2, '=IF(ISNUMBER(B22),DATE(YEAR(B6),MONTH(B6)+B22-1,1),"")', "mmm yyyy")
    put(ws, 24, 1, "Total paid (approx.)")
    put(ws, 24, 2, f"=SUM(Schedule!M5:M{4 + M})", MONEY)
    put(ws, 25, 1, "Interest (approx.)")
    put(ws, 25, 2, "=B24-B19", MONEY)
    sc = wb.create_sheet("Schedule")
    sheet_base(sc, "Schedule", "Balance of each debt at the end of every month", [8] + [12] * N + [8, 13])
    header(sc, 4, ["Month"] + [f"Debt {i + 1}" for i in range(N)] + ["Focus", "Paid"])
    for m in range(M):
        r = 5 + m
        sc.cell(row=r, column=1, value=m + 1).font = BODY
        prev = [f"Plan!$B${9 + j}" if m == 0 else f"{get_column_letter(2 + j)}{r - 1}" for j in range(N)]
        focus = "MIN(" + ",".join(f"IF(N({prev[j]})>0,Plan!$E${9 + j},999)" for j in range(N)) + ")"
        sc.cell(row=r, column=12, value=f"={focus}").font = CALC
        freed = "+".join(f"IF(AND(N(Plan!$B${9 + j})>0,N({prev[j]})<=0),Plan!$D${9 + j},0)" for j in range(N))
        for j in range(N):
            pay = f"(Plan!$D${9 + j}+IF(Plan!$E${9 + j}=$L{r},Plan!$B$5+{freed},0))"
            c = sc.cell(row=r, column=2 + j, value=f"=IF(N({prev[j]})<=0,0,MAX(0,{prev[j]}*(1+Plan!$C${9 + j}/12)-{pay}))")
            c.font, c.number_format = CALC, '"$"#,##0'
        paid = "+".join(f"IF(N({prev[j]})<=0,0,MIN({prev[j]}*(1+Plan!$C${9 + j}/12),Plan!$D${9 + j}+IF(Plan!$E${9 + j}=$L{r},Plan!$B$5+{freed},0)))" for j in range(N))
        c = sc.cell(row=r, column=13, value=f"={paid}")
        c.font, c.number_format = CALC, '"$"#,##0'
    return {"sheets": ["Start here", "Plan", "Schedule"], "sample_rows": 6, "checks": [("Plan", "E9"), ("Plan", "F9"), ("Plan", "B22"), ("Plan", "B25")]}

def meal_planner(wb):
    start_here(wb, "Meal Planner + Grocery List", "Plan breakfast, lunch, dinner and snacks for 7 days and keep a grocery list grouped by aisle with a running total.",
               ["Type meals into the Week grid.", "Add ingredients to Groceries with aisle, quantity and price.", "Tick Got it as you shop; the remaining total updates."],
               ["Aisles are a dropdown – edit the list on the Groceries sheet, column H.", "Duplicate the sheet for each new week."])
    ws = wb.create_sheet("Week")
    sheet_base(ws, "Meals this week", "Week of 19 Oct 2026", [12, 22, 22, 22, 22, 22, 22, 22])
    header(ws, 4, ["", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    meals = {"Breakfast": ["Oats + berries", "Eggs + toast", "Yogurt + granola", "Oats + banana", "Smoothie", "Pancakes", "Eggs + avocado"],
             "Lunch": ["Chicken wrap", "Leftover chili", "Tuna salad", "Lentil soup", "Chicken wrap", "Out", "Soup + bread"],
             "Dinner": ["Chili", "Salmon + rice", "Stir-fry", "Pasta + salad", "Tacos", "Pizza night", "Roast chicken"],
             "Snack": ["Apple", "Nuts", "Hummus + carrots", "Cheese", "Fruit", "Popcorn", "Yogurt"]}
    for i, (meal, row) in enumerate(meals.items()):
        put(ws, 5 + i, 1, meal).font = Font(bold=True, size=10)
        for d, v in enumerate(row):
            put(ws, 5 + i, 2 + d, v, inp=True)
    gs = wb.create_sheet("Groceries")
    sheet_base(gs, "Grocery list", "Grouped by aisle", [24, 14, 8, 10, 10, 12, 4, 16])
    header(gs, 4, ["Item", "Aisle", "Qty", "Price", "Got it", "Line total"])
    aisles = ["Produce", "Meat & fish", "Dairy & eggs", "Bakery", "Pantry", "Frozen", "Other"]
    for i, a in enumerate(aisles):
        put(gs, 5 + i, 8, a, inp=True)
    gs["H4"] = "Aisles"
    gs["H4"].font = LABEL
    items = [("Berries", "Produce", 2, 3.5), ("Bananas", "Produce", 6, 0.3), ("Avocados", "Produce", 3, 1.2), ("Carrots", "Produce", 1, 1.5), ("Salad mix", "Produce", 2, 3),
             ("Chicken breast", "Meat & fish", 2, 7.5), ("Salmon", "Meat & fish", 1, 11), ("Ground beef", "Meat & fish", 1, 6), ("Eggs (12)", "Dairy & eggs", 1, 4.2),
             ("Greek yogurt", "Dairy & eggs", 2, 4.5), ("Cheese", "Dairy & eggs", 1, 5), ("Bread", "Bakery", 1, 3.8), ("Tortillas", "Bakery", 2, 2.9),
             ("Oats", "Pantry", 1, 3.5), ("Rice", "Pantry", 1, 2.8), ("Pasta", "Pantry", 2, 1.6), ("Lentils", "Pantry", 1, 2.2), ("Beans", "Pantry", 3, 1.1),
             ("Pizza dough", "Frozen", 1, 3), ("Frozen veg", "Frozen", 2, 2.5)]
    for i, (n, a, q, p) in enumerate(items):
        r = 5 + i
        put(gs, r, 1, n, inp=True)
        put(gs, r, 2, a, inp=True)
        put(gs, r, 3, q, inp=True)
        put(gs, r, 4, p, MONEY, True)
        put(gs, r, 5, "x" if i % 3 == 0 else None, inp=True)
        put(gs, r, 6, f"=C{r}*D{r}", MONEY)
    dv = DataValidation(type="list", formula1="=$H$5:$H$15", allow_blank=True)
    gs.add_data_validation(dv)
    dv.add("B5:B200")
    put(gs, 27, 1, "List total")
    put(gs, 27, 6, "=SUM(F5:F200)", MONEY)
    put(gs, 28, 1, "Still to buy")
    put(gs, 28, 6, '=SUMIFS(F5:F200,E5:E200,"<>x")', MONEY)
    gs.conditional_formatting.add("A5:F200", FormulaRule(formula=['$E5="x"'], font=Font(color="AAAAAA", strike=True)))
    return {"sheets": ["Start here", "Week", "Groceries"], "sample_rows": 20, "checks": [("Groceries", "F27"), ("Groceries", "F28")]}


def reading_log(wb):
    start_here(wb, "Reading Log", "Log the books you read, rate them, and watch your yearly goal fill up – with pages read and books per month.",
               ["Set your yearly goal in Stats!B4.", "Add each book on Books with the finish date, pages and a 1–5 rating.", "Stats shows progress, pages and your monthly count."],
               ["Leave the finish date blank for books you are still reading.", "Delete sample rows (5–29) to start your own year."])
    bs = wb.create_sheet("Books")
    sheet_base(bs, "Books", "2026", [32, 22, 14, 9, 8, 12, 30])
    header(bs, 4, ["Title", "Author", "Finished", "Pages", "Rating", "Format", "Note"])
    import random
    rnd = random.Random(5)
    for i in range(25):
        r = 5 + i
        put(bs, r, 1, f"Sample book {i + 1}", inp=True)
        put(bs, r, 2, f"Author {chr(65 + i % 20)}", inp=True)
        put(bs, r, 3, datetime.date(2026, 1 + i // 3, 3 + (i * 5) % 25) if i < 22 else None, "yyyy-mm-dd", True)
        put(bs, r, 4, rnd.randint(140, 520), inp=True)
        put(bs, r, 5, rnd.randint(2, 5), inp=True)
        put(bs, r, 6, rnd.choice(["Print", "Ebook", "Audio"]), inp=True)
    fv = DataValidation(type="list", formula1='"Print,Ebook,Audio"')
    rv = DataValidation(type="whole", operator="between", formula1="1", formula2="5")
    bs.add_data_validation(fv)
    bs.add_data_validation(rv)
    fv.add("F5:F500")
    rv.add("E5:E500")
    st = wb.create_sheet("Stats", 1)
    sheet_base(st, "Stats", "Your year in books", [22, 14, 4, 12, 12])
    rows = [("Yearly goal", 30, None), ("Books finished", "=COUNT(Books!C5:C500)", None), ("Goal reached", "=IF(B4=0,0,MIN(1,B5/B4))", PCT),
            ("Pages read", '=SUMIFS(Books!D5:D500,Books!C5:C500,"<>")', "#,##0"), ("Average rating", '=IFERROR(AVERAGEIFS(Books!E5:E500,Books!C5:C500,"<>"),0)', "0.0"),
            ("Still reading", '=COUNTIFS(Books!A5:A500,"<>",Books!C5:C500,"")', None)]
    for i, (lab, v, fmt) in enumerate(rows):
        put(st, 4 + i, 1, lab)
        put(st, 4 + i, 2, v, fmt, inp=(i == 0))
    st.conditional_formatting.add("B6", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=ACCENT))
    header(st, 12, ["", "", "", "Month", "Books"])
    st.freeze_panes = None
    for m in range(12):
        r = 13 + m
        put(st, r, 4, datetime.date(2026, m + 1, 1).strftime("%b"))
        put(st, r, 5, f'=COUNTIFS(Books!$C$5:$C$500,">="&DATE(2026,{m + 1},1),Books!$C$5:$C$500,"<"&DATE(2026,{m + 2 if m < 11 else 1},1)+{0 if m < 11 else 365})')
    ch = BarChart()
    ch.title = "Books per month"
    ch.add_data(Reference(st, min_col=5, min_row=12, max_row=24), titles_from_data=True)
    ch.set_categories(Reference(st, min_col=4, min_row=13, max_row=24))
    ch.height, ch.width = 7, 12
    st.add_chart(ch, "G4")
    return {"sheets": ["Start here", "Stats", "Books"], "sample_rows": 25, "checks": [("Stats", "B5"), ("Stats", "B6"), ("Stats", "B7"), ("Stats", "E13")]}


def expense_tracker(wb):
    start_here(wb, "Expense Tracker", "Log expenses with a category dropdown and see totals by category and by month for the whole year, with a chart.",
               ["Add each expense on Expenses: date, category, amount, payment method.", "Summary fills in totals per category and month automatically.", "Edit the category list on Summary column A."],
               ["Works for any currency – change the number format if you like.", "Delete the sample rows (5–104) to start fresh."])
    ex = wb.create_sheet("Expenses")
    sheet_base(ex, "Expenses", "One line per expense", [14, 20, 13, 14, 30])
    header(ex, 4, ["Date", "Category", "Amount", "Paid with", "Note"])
    cats = ["Housing", "Food", "Transport", "Health", "Fun", "Shopping", "Bills", "Other"]
    import random
    rnd = random.Random(9)
    for i in range(100):
        r = 5 + i
        put(ex, r, 1, datetime.date(2026, 1 + i // 10, 1 + (i * 7) % 28), "yyyy-mm-dd", True)
        put(ex, r, 2, rnd.choice(cats), inp=True)
        put(ex, r, 3, round(rnd.uniform(4, 180), 2), MONEY, True)
        put(ex, r, 4, rnd.choice(["Card", "Cash", "Transfer"]), inp=True)
    sm = wb.create_sheet("Summary", 1)
    sheet_base(sm, "Summary", "2026 by category and month", [16] + [10] * 12 + [12])
    header(sm, 4, ["Category"] + [datetime.date(2026, m, 1).strftime("%b") for m in range(1, 13)] + ["Year"])
    for i, c in enumerate(cats):
        r = 5 + i
        put(sm, r, 1, c, inp=True)
        for m in range(12):
            nxt = f"DATE(2026,{m + 2},1)" if m < 11 else "DATE(2027,1,1)"
            put(sm, r, 2 + m, f'=SUMIFS(Expenses!$C$5:$C$1000,Expenses!$B$5:$B$1000,$A{r},Expenses!$A$5:$A$1000,">="&DATE(2026,{m + 1},1),Expenses!$A$5:$A$1000,"<"&{nxt})', '"$"#,##0')
        put(sm, r, 14, f"=SUM(B{r}:M{r})", '"$"#,##0')
    put(sm, 13, 1, "Total")
    for col in range(2, 15):
        L = get_column_letter(col)
        put(sm, 13, col, f"=SUM({L}5:{L}12)", '"$"#,##0')
    dv = DataValidation(type="list", formula1="=Summary!$A$5:$A$12", allow_blank=True)
    ex.add_data_validation(dv)
    dv.add("B5:B1000")
    pv = DataValidation(type="list", formula1='"Card,Cash,Transfer"', allow_blank=True)
    ex.add_data_validation(pv)
    pv.add("D5:D1000")
    ch = BarChart()
    ch.title = "Spending by category"
    ch.add_data(Reference(sm, min_col=14, min_row=4, max_row=12), titles_from_data=True)
    ch.set_categories(Reference(sm, min_col=1, min_row=5, max_row=12))
    ch.height, ch.width = 7, 14
    sm.add_chart(ch, "A16")
    return {"sheets": ["Start here", "Summary", "Expenses"], "sample_rows": 100, "checks": [("Summary", "N13"), ("Summary", "B5"), ("Summary", "N5")]}


CATALOG = {
    "monthly-budget": ("Monthly Budget 50/30/20", monthly_budget, "Plan your month and see where every dollar goes", ["budget", "50/30/20", "personal finance", "google sheets", "excel"]),
    "habit-tracker": ("Monthly Habit Tracker", habit_tracker, "Twelve habits, daily ticks, streaks and % done", ["habit tracker", "productivity", "self improvement", "google sheets", "excel"]),
    "weekly-planner": ("Weekly Planner", weekly_planner, "Top 3, daily to-dos and a progress count", ["weekly planner", "to do list", "productivity", "google sheets", "excel"]),
    "savings-goals": ("Savings Goals Tracker", savings_goals, "Several goals, deposits, months to finish", ["savings tracker", "sinking funds", "goals", "google sheets", "excel"]),
    "debt-payoff": ("Debt Payoff Planner", debt_snowball, "Snowball or avalanche order with months per debt", ["debt snowball", "debt avalanche", "debt payoff", "google sheets", "excel"]),
    "meal-planner": ("Meal Planner + Grocery List", meal_planner, "Seven days of meals and a smart shopping list", ["meal planner", "grocery list", "meal prep", "google sheets", "excel"]),
    "reading-log": ("Reading Log", reading_log, "Yearly goal, ratings and books per month", ["reading log", "book tracker", "reading goal", "google sheets", "excel"]),
    "expense-tracker": ("Expense Tracker", expense_tracker, "Categories by month for the whole year", ["expense tracker", "spending log", "budget", "google sheets", "excel"]),
}


def build(slug, out):
    title, fn, tagline, tags = CATALOG[slug]
    wb = Workbook()
    info = fn(wb)
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = ACCENT if ws.title == "Start here" else LINE
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{slug}.xlsx"
    wb.save(path)
    return path, info, title, tagline, tags


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    for s in (CATALOG if target == "all" else [target]):
        p, info, *_ = build(s, ROOT / "_tam" / s)
        print(s, p, info)
