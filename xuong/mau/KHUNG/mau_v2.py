"""Khuôn Mẫu v2 (24/10/2026, sau 4 mẫu bị Cửa 1 trả: tên không khớp nội dung, giá trị mỏng).
Mỗi mẫu = công cụ thật có công thức tính (không phải 12 tab tháng giống nhau). Chỉ dùng hàm chạy được ở Excel 2016+ VÀ Google Sheets
(không UNIQUE/FILTER/LET/MINIFS) để nhập vào Sheets không vỡ công thức.
  python xuong/mau/KHUNG/mau_v2.py <debt|meal|savings|weekly> <out.xlsx>
"""
import datetime as dt
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

INK, SOFT, LINE = "1D1D1F", "6E6E73", "E5E5EA"
F_TITLE, F_SUB, F_HEAD, F_BODY = Font(name="Arial", size=20, bold=True, color=INK), Font(name="Arial", size=11, color=SOFT), Font(name="Arial", size=10, bold=True, color=SOFT), Font(name="Arial", size=11, color=INK)
INPUT = PatternFill("solid", fgColor="EEF4FF")  # ô khách gõ
KPI = PatternFill("solid", fgColor="F5F5F7")
BOT = Border(bottom=Side(style="thin", color=LINE))
USD, PCT, DATE = '"$"#,##0.00', "0%", "mmm d, yyyy"


def sheet(wb, title, head, sub, accent, widths):
    ws = wb.create_sheet(title) if wb.worksheets[0].title != "Sheet" else wb.worksheets[0]
    ws.title = title
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = accent
    ws["A1"], ws["A2"] = head, sub
    ws["A1"].font, ws["A2"].font = F_TITLE, F_SUB
    ws.row_dimensions[1].height = 30
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[L(i)].width = w
    return ws


def header(ws, row, cols, start=1):
    for i, c in enumerate(cols):
        x = ws.cell(row, start + i, c)
        x.font, x.border, x.alignment = F_HEAD, BOT, Alignment(wrap_text=True, vertical="bottom")


def put(ws, ref, v, fmt=None, fill=None, font=None):
    c = ws[ref]
    c.value = v
    c.font = font or F_BODY
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    return c


def kpi(ws, row, col, label, formula, fmt, accent):
    put(ws, f"{L(col)}{row}", label, font=F_HEAD, fill=KPI)
    put(ws, f"{L(col)}{row + 1}", formula, fmt, KPI, Font(name="Arial", size=18, bold=True, color=accent))


def guide(wb, title, what, steps, accent, notes=()):
    ws = sheet(wb, "Start here", title, "Free template · templates.snoutsmith.com · Excel 2016+ and Google Sheets", accent, [100])
    r = 4
    for h, lines in (("WHAT IT DOES", [what]), ("HOW TO USE", steps), ("GOOD TO KNOW", list(notes) + [
            "Blue cells are the only cells you type in; everything else calculates.",
            "Google Sheets: File → Import → Upload → 'Replace spreadsheet'. All formulas are Sheets-compatible (no add-ons, no scripts).",
            "Sample data is filled in so you can see it working – select the blue cells and press Delete to start fresh."])):
        put(ws, f"A{r}", h, font=Font(name="Arial", size=10, bold=True, color=accent)); r += 1
        for t in lines:
            put(ws, f"A{r}", t).alignment = Alignment(wrap_text=True); r += 1
        r += 1
    return ws


# ---------------------------------------------------------------- 1. Debt payoff (snowball / avalanche)
def debt(path):
    A = "B42318"; wb = Workbook(); N, M = 8, 120
    guide(wb, "Debt Payoff Planner 2026 – Snowball & Avalanche",
          "Enter your debts once (balance, APR, minimum payment) and one extra amount per month. The planner simulates every month: interest, payment and remaining balance for each debt, rolls freed-up minimums onto the next target, and tells you your debt-free month and total interest – for the Snowball (smallest balance first) or Avalanche (highest APR first) method.",
          ["1. Debts tab: type each debt's name, current balance, APR % and minimum monthly payment (up to 8 debts).",
           "2. Type your extra monthly payment and choose Snowball or Avalanche in the blue dropdown.",
           "3. Dashboard shows debt-free date, months, total interest and each debt's payoff month; switch the method to compare.",
           "4. Each month, log what you actually paid on the Payments tab – the Dashboard compares actual vs plan."], A,
          ["Interest is estimated monthly as balance × APR ÷ 12 (how most cards and loans accrue). Your lender's statement is the final number.",
           "This is a planning tool, not financial advice."])
    ws = sheet(wb, "Debts", "Your debts", "Type in the blue cells", A, [24, 16, 10, 16, 14, 14, 14])
    put(ws, "A4", "Extra payment per month", font=F_HEAD); put(ws, "B4", 300, USD, INPUT)
    put(ws, "A5", "Method", font=F_HEAD); put(ws, "B5", "Avalanche", fill=INPUT)
    dv = DataValidation(type="list", formula1='"Snowball,Avalanche"', allow_blank=False); ws.add_data_validation(dv); dv.add("B5")
    put(ws, "A6", "Start month", font=F_HEAD); put(ws, "B6", dt.date(2026, 11, 1), DATE, INPUT)
    header(ws, 8, ["Debt", "Balance", "APR %", "Min. payment", "Priority", "Payoff month", "Interest paid"])
    sample = [("Store card", 1200, 26.99, 40), ("Credit card", 4200, 22.9, 110), ("Car loan", 9800, 7.4, 260), ("Student loan", 15200, 5.5, 170), ("Medical bill", 650, 0, 50)]
    for i in range(N):
        r = 9 + i
        if i < len(sample):
            for j, v in enumerate(sample[i]):
                put(ws, f"{L(j + 1)}{r}", v, [None, USD, "0.00", USD][j], INPUT)
        else:
            for j in range(4): put(ws, f"{L(j + 1)}{r}", None, [None, USD, "0.00", USD][j], INPUT)
        # priority: snowball = rank by balance asc, avalanche = rank by APR desc; ties broken by row
        put(ws, f"E{r}", f'=IF(B{r}>0,IF($B$5="Snowball",COUNTIFS($B$9:$B${8 + N},">0",$B$9:$B${8 + N},"<"&B{r})+COUNTIFS($B$8:B{r - 1},B{r}),COUNTIFS($B$9:$B${8 + N},">0",$C$9:$C${8 + N},">"&C{r})+COUNTIFS($B$8:B{r - 1},">0",$C$8:C{r - 1},C{r}))+1,"")')
    put(ws, "A18", "Minimum payments total", font=F_HEAD); put(ws, "D18", f"=SUM(D9:D{8 + N})", USD)
    put(ws, "A19", "Monthly budget for debt", font=F_HEAD); put(ws, "D19", "=D18+B4", USD)
    # ---- Plan: per month, per debt: balance start, interest, payment
    pl = sheet(wb, "Plan", "Month-by-month plan", "Calculated – nothing to type. Freed-up minimums roll onto the next target debt.", A, [12, 12] + [11] * (3 * N + N + 4))
    cols = {}
    head = ["Month", "Target #"]
    for i in range(N):
        head += [f"D{i + 1} start", f"D{i + 1} interest", f"D{i + 1} paid"]
    head += [f"key{i + 1}" for i in range(N)] + ["Total start", "Total paid", "Interest", "Total end"]
    header(pl, 4, head)
    c0 = 3
    for i in range(N):
        cols[i] = (L(c0 + 3 * i), L(c0 + 3 * i + 1), L(c0 + 3 * i + 2))
    kc = [L(c0 + 3 * N + i) for i in range(N)]
    TS, TP, TI, TE = [L(c0 + 4 * N + k) for k in range(4)]
    for m in range(M):
        r = 5 + m
        put(pl, f"A{r}", f"=EDATE(Debts!$B$6,{m})", "mmm yyyy")
        for i in range(N):
            S, I, P = cols[i]; dr = 9 + i
            start = f"=MAX(0,Debts!B{dr})" if m == 0 else f"=MAX(0,ROUND({S}{r - 1}+{I}{r - 1}-{P}{r - 1},2))"
            put(pl, f"{S}{r}", start, USD)
            put(pl, f"{I}{r}", f"=ROUND({S}{r}*Debts!C{dr}/1200,2)", USD)
            put(pl, f"{kc[i]}{r}", f'=IF({S}{r}>0.004,Debts!E{dr},99)')
        put(pl, f"B{r}", f"=MIN({kc[0]}{r}:{kc[-1]}{r})")
        # pool = extra + minimums of debts already at 0 this month
        pool = "Debts!$B$4+" + "+".join(f"IF({cols[i][0]}{r}<=0.004,Debts!$D${9 + i},0)" for i in range(N))
        for i in range(N):
            S, I, P = cols[i]; dr = 9 + i
            base = f"MIN(Debts!D{dr},{S}{r}+{I}{r})"
            put(pl, f"{P}{r}", f"=IF({S}{r}<=0.004,0,{base}+IF({kc[i]}{r}=$B{r},MIN({pool},{S}{r}+{I}{r}-{base}),0))", USD)
        put(pl, f"{TS}{r}", "=" + "+".join(f"{cols[i][0]}{r}" for i in range(N)), USD)
        put(pl, f"{TP}{r}", "=" + "+".join(f"{cols[i][2]}{r}" for i in range(N)), USD)
        put(pl, f"{TI}{r}", "=" + "+".join(f"{cols[i][1]}{r}" for i in range(N)), USD)
        put(pl, f"{TE}{r}", f"=MAX(0,{TS}{r}+{TI}{r}-{TP}{r})", USD)
    pl.freeze_panes = "C5"
    last = 4 + M
    for i in range(N):
        S, I, P = cols[i]; r = 9 + i
        ws[f"F{r}"] = f'=IF(B{r}>0,IFERROR(INDEX(Plan!$A$5:$A${last},MATCH(0,Plan!{S}$6:{S}${last + 1},0)),"> 10 yrs"),"")'
        ws[f"F{r}"].number_format = "mmm yyyy"
        ws[f"G{r}"] = f'=IF(B{r}>0,SUM(Plan!{I}$5:{I}${last}),"")'; ws[f"G{r}"].number_format = USD
    # ---- Payments log
    pay = sheet(wb, "Payments", "Payments you made", "One line per payment – Dashboard compares with the plan", A, [14, 22, 14, 30])
    header(pay, 4, ["Date", "Debt", "Amount", "Note"])
    dvd = DataValidation(type="list", formula1="=Debts!$A$9:$A$16"); pay.add_data_validation(dvd)
    plog = [(dt.date(2026, 11, 3), "Store card", 340), (dt.date(2026, 11, 5), "Credit card", 110), (dt.date(2026, 11, 12), "Car loan", 260), (dt.date(2026, 11, 15), "Student loan", 170), (dt.date(2026, 11, 20), "Medical bill", 50)]
    for k in range(200):
        r = 5 + k
        for j in range(4): put(pay, f"{L(j + 1)}{r}", plog[k][j] if k < len(plog) and j < 3 else None, [DATE, None, USD, None][j], INPUT)
        dvd.add(f"B{r}")
    # ---- Dashboard
    db = sheet(wb, "Dashboard", "Debt-free plan", "Change the method or extra payment on Debts and watch these update", A, [22, 18, 18, 18, 18])
    kpi(db, 4, 1, "DEBT-FREE MONTH", f'=IFERROR(INDEX(Plan!A5:A{last},MATCH(0,Plan!{TE}5:{TE}{last},0)),"> 10 years")', "mmm yyyy", A)
    kpi(db, 4, 2, "MONTHS TO GO", f'=IFERROR(MATCH(0,Plan!{TE}5:{TE}{last},0),">120")', "0", A)
    kpi(db, 4, 3, "TOTAL INTEREST", f"=SUM(Plan!{TI}5:{TI}{last})", USD, A)
    kpi(db, 4, 4, "TOTAL DEBT NOW", "=SUM(Debts!B9:B16)", USD, A)
    kpi(db, 4, 5, "METHOD", "=Debts!B5", None, A)
    header(db, 8, ["Month", "Planned payment", "Actually paid", "Difference", "Balance left (plan)"])
    for m in range(12):
        r = 9 + m
        put(db, f"A{r}", f"=Plan!A{5 + m}", "mmm yyyy")
        put(db, f"B{r}", f"=Plan!{TP}{5 + m}", USD)
        put(db, f"C{r}", f'=SUMPRODUCT((Payments!$A$5:$A$204>=A{r})*(Payments!$A$5:$A$204<EDATE(A{r},1))*Payments!$C$5:$C$204)', USD)
        put(db, f"D{r}", f'=IF(C{r}=0,"",C{r}-B{r})', USD)
        put(db, f"E{r}", f"=Plan!{TE}{5 + m}", USD)
    db.conditional_formatting.add("D9:D20", CellIsRule(operator="lessThan", formula=["0"], font=Font(color=A, bold=True)))
    ch = LineChart(); ch.title = "Total balance (plan)"; ch.height, ch.width = 8, 18; ch.y_axis.numFmt = '"$"#,##0'
    ch.add_data(Reference(pl, min_col=pl[f"{TE}4"].column, min_row=4, max_row=4 + 60), titles_from_data=True)
    ch.set_categories(Reference(pl, min_col=1, min_row=5, max_row=4 + 60)); ch.legend = None
    db.add_chart(ch, "G4")
    wb.move_sheet("Dashboard", -(len(wb.sheetnames) - 2))
    wb.save(path)


# ---------------------------------------------------------------- 2. Meal planner + grocery list
RECIPES = [  # name, meal, servings, cost/serving USD (editable estimate), ingredients
    ("Overnight oats", "Breakfast", 1, 1.10, "Oats|Milk|Yogurt|Berries|Honey"), ("Scrambled eggs & toast", "Breakfast", 1, 1.30, "Eggs|Bread|Butter|Milk"),
    ("Greek yogurt bowl", "Breakfast", 1, 1.60, "Yogurt|Granola|Berries|Honey"), ("Banana pancakes", "Breakfast", 2, 0.90, "Flour|Eggs|Milk|Bananas|Butter"),
    ("Avocado toast", "Breakfast", 1, 1.90, "Bread|Avocado|Eggs|Lemon"), ("Peanut butter banana toast", "Breakfast", 1, 0.80, "Bread|Peanut butter|Bananas"),
    ("Veggie omelette", "Breakfast", 1, 1.50, "Eggs|Bell pepper|Onion|Cheese|Spinach"), ("Smoothie", "Breakfast", 1, 1.70, "Bananas|Berries|Milk|Yogurt|Spinach"),
    ("Breakfast burrito", "Breakfast", 2, 1.80, "Tortillas|Eggs|Black beans|Cheese|Salsa"), ("Cereal & fruit", "Breakfast", 1, 0.90, "Cereal|Milk|Bananas"),
    ("Chicken Caesar wrap", "Lunch", 2, 2.70, "Tortillas|Chicken breast|Lettuce|Parmesan|Caesar dressing"), ("Tuna salad sandwich", "Lunch", 2, 1.90, "Bread|Canned tuna|Mayonnaise|Celery|Lettuce"),
    ("Lentil soup", "Lunch", 4, 1.20, "Lentils|Carrots|Onion|Celery|Canned tomatoes"), ("Quinoa salad", "Lunch", 3, 2.10, "Quinoa|Cucumber|Tomatoes|Feta|Lemon"),
    ("Grilled cheese & tomato soup", "Lunch", 2, 1.60, "Bread|Cheese|Butter|Canned tomatoes|Onion"), ("Chicken noodle soup", "Lunch", 4, 1.90, "Chicken breast|Egg noodles|Carrots|Celery|Onion"),
    ("Hummus veggie plate", "Lunch", 1, 2.20, "Hummus|Carrots|Cucumber|Bell pepper|Pita"), ("Black bean quesadilla", "Lunch", 2, 1.40, "Tortillas|Black beans|Cheese|Salsa"),
    ("Egg fried rice", "Lunch", 2, 1.30, "Rice|Eggs|Frozen peas|Soy sauce|Onion"), ("Turkey club sandwich", "Lunch", 2, 2.60, "Bread|Sliced turkey|Bacon|Lettuce|Tomatoes"),
    ("Caprese pasta salad", "Lunch", 3, 2.00, "Pasta|Tomatoes|Mozzarella|Basil|Olive oil"), ("Leftovers", "Lunch", 1, 0.00, ""),
    ("Spaghetti bolognese", "Dinner", 4, 2.40, "Pasta|Ground beef|Canned tomatoes|Onion|Garlic"), ("Sheet-pan chicken & veg", "Dinner", 4, 3.10, "Chicken thighs|Potatoes|Broccoli|Olive oil|Garlic"),
    ("Beef tacos", "Dinner", 4, 2.80, "Tortillas|Ground beef|Lettuce|Cheese|Salsa"), ("Salmon, rice & greens", "Dinner", 2, 5.20, "Salmon|Rice|Green beans|Lemon|Butter"),
    ("Vegetable stir-fry", "Dinner", 3, 2.00, "Rice|Broccoli|Bell pepper|Carrots|Soy sauce"), ("Chicken curry", "Dinner", 4, 2.60, "Chicken thighs|Coconut milk|Onion|Curry paste|Rice"),
    ("Chili con carne", "Dinner", 6, 2.10, "Ground beef|Kidney beans|Canned tomatoes|Onion|Chili powder"), ("Homemade pizza", "Dinner", 4, 2.30, "Pizza dough|Mozzarella|Canned tomatoes|Pepperoni|Basil"),
    ("Baked potatoes & chili", "Dinner", 4, 1.70, "Potatoes|Kidney beans|Cheese|Sour cream"), ("Shrimp garlic pasta", "Dinner", 3, 4.10, "Pasta|Shrimp|Garlic|Butter|Parmesan"),
    ("Pork chops & apples", "Dinner", 4, 3.40, "Pork chops|Apples|Onion|Potatoes|Butter"), ("Lentil dal", "Dinner", 4, 1.30, "Lentils|Onion|Garlic|Coconut milk|Rice"),
    ("Burgers & salad", "Dinner", 4, 3.20, "Ground beef|Burger buns|Cheese|Lettuce|Tomatoes"), ("Chicken fajitas", "Dinner", 4, 3.00, "Chicken breast|Tortillas|Bell pepper|Onion|Sour cream"),
    ("Mac & cheese with peas", "Dinner", 4, 1.60, "Pasta|Cheese|Milk|Butter|Frozen peas"), ("Teriyaki chicken bowl", "Dinner", 4, 2.70, "Chicken thighs|Rice|Teriyaki sauce|Broccoli|Carrots"),
    ("Minestrone", "Dinner", 6, 1.50, "Pasta|Kidney beans|Carrots|Celery|Canned tomatoes"), ("Fish tacos", "Dinner", 4, 3.60, "White fish|Tortillas|Cabbage|Lime|Sour cream"),
    ("Stuffed peppers", "Dinner", 4, 2.90, "Bell pepper|Ground beef|Rice|Canned tomatoes|Cheese"), ("Pesto gnocchi", "Dinner", 3, 2.50, "Gnocchi|Pesto|Tomatoes|Parmesan|Spinach"),
    ("Roast chicken dinner", "Dinner", 6, 2.80, "Whole chicken|Potatoes|Carrots|Onion|Butter"), ("Beef & broccoli", "Dinner", 4, 3.30, "Beef strips|Broccoli|Soy sauce|Garlic|Rice"),
    ("Veggie burrito bowls", "Dinner", 4, 2.00, "Rice|Black beans|Corn|Salsa|Avocado"), ("Tomato basil soup & bread", "Dinner", 4, 1.40, "Canned tomatoes|Onion|Basil|Bread|Cream"),
    ("Sausage & peppers", "Dinner", 4, 2.60, "Sausages|Bell pepper|Onion|Burger buns"), ("Eat out / takeaway", "Dinner", 1, 0.00, ""),
    ("Apple & peanut butter", "Snack", 1, 0.70, "Apples|Peanut butter"), ("Trail mix", "Snack", 4, 0.90, "Nuts|Raisins|Chocolate chips"),
    ("Cheese & crackers", "Snack", 2, 1.10, "Cheese|Crackers"), ("Veggies & hummus", "Snack", 2, 1.00, "Carrots|Cucumber|Hummus"),
    ("Popcorn", "Snack", 4, 0.30, "Popcorn kernels|Butter"), ("Yogurt & honey", "Snack", 1, 0.90, "Yogurt|Honey"),
    ("Banana", "Snack", 1, 0.30, "Bananas"), ("Hard-boiled eggs", "Snack", 2, 0.50, "Eggs"), ("Energy balls", "Snack", 6, 0.60, "Oats|Peanut butter|Honey|Chocolate chips"),
    ("Fruit salad", "Snack", 4, 1.20, "Apples|Bananas|Berries|Grapes"), ("Rice cakes & avocado", "Snack", 1, 1.00, "Rice cakes|Avocado"),
]
AISLE = {"Produce": "Berries Bananas Avocado Lemon Lime Bell pepper Onion Spinach Lettuce Celery Carrots Cucumber Tomatoes Basil Garlic Potatoes Broccoli Green beans Apples Cabbage Corn Grapes",
         "Dairy & eggs": "Milk Yogurt Eggs Butter Cheese Parmesan Feta Mozzarella Sour cream Cream",
         "Meat & fish": "Chicken breast Chicken thighs Ground beef Salmon Shrimp Pork chops Sliced turkey Bacon Pepperoni White fish Whole chicken Beef strips Sausages",
         "Bakery": "Bread Tortillas Pita Burger buns Pizza dough"}


def aisle(x):
    for k, v in AISLE.items():
        if x in v: return k
    return "Pantry"


def meal(path):
    A = "1E7B34"; wb = Workbook()
    guide(wb, "Meal Planner & Auto Grocery List – 4 Weeks",
          "Pick meals from a 60-recipe library for breakfast, lunch, dinner and a snack, 7 days a week for 4 weeks. Each week shows its estimated food cost against your budget, and the Grocery List tab builds the shopping list for the week you choose – every ingredient you need, grouped by aisle, with how many planned meals use it.",
          ["1. Settings: type your weekly food budget and how many people you cook for.",
           "2. Week 1–4 tabs: choose a meal in each blue cell from the dropdown (or type your own recipe on the Recipes tab first).",
           "3. Grocery List: pick the week number at the top – the list fills itself; tick 'Got it' while you shop.",
           "4. Recipes: edit costs to match your store, or add up to 40 of your own recipes with up to 5 main ingredients."], A,
          ["Costs per serving are editable US estimates (2026) – change them to your store's prices for accurate totals.",
           "Pantry staples (salt, oil, spices) are not listed unless they are a main ingredient."])
    st = sheet(wb, "Settings", "Settings", "Type in the blue cells", A, [30, 16])
    put(st, "A4", "Weekly food budget", font=F_HEAD); put(st, "B4", 120, USD, INPUT)
    put(st, "A5", "People you cook for", font=F_HEAD); put(st, "B5", 2, "0", INPUT)
    rc = sheet(wb, "Recipes", "Recipe library", "60 starter recipes – edit costs, add your own in the blue rows", A, [30, 12, 10, 14, 16, 16, 16, 16, 16])
    header(rc, 4, ["Meal", "Type", "Serves", "Cost / serving", "Ingredient 1", "Ingredient 2", "Ingredient 3", "Ingredient 4", "Ingredient 5"])
    NR = 100
    for k in range(NR):
        r = 5 + k
        if k < len(RECIPES):
            n, t, s, c, ing = RECIPES[k]; ings = ing.split("|") if ing else []
            vals = [n, t, s, c] + ings + [None] * (5 - len(ings))
            for j, v in enumerate(vals): put(rc, f"{L(j + 1)}{r}", v, USD if j == 3 else None)
        else:
            for j in range(9): put(rc, f"{L(j + 1)}{r}", None, USD if j == 3 else None, INPUT)
    LAST = 4 + NR
    dv = DataValidation(type="list", formula1=f"=Recipes!$A$5:$A${LAST}", allow_blank=True)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    slots = ["Breakfast", "Lunch", "Dinner", "Snack"]
    import random
    rnd = random.Random(7)
    bytype = {t: [x[0] for x in RECIPES if x[1] == t] for t in slots}
    for w in range(1, 5):
        ws = sheet(wb, f"Week {w}", f"Week {w}", "Choose a meal in each blue cell – cost and grocery list update", A, [12] + [26, 10] * 4)
        ws.add_data_validation(dv)
        header(ws, 4, ["Day"] + sum([[s, "Cost"] for s in slots], []))
        for d, day in enumerate(days):
            r = 5 + d
            put(ws, f"A{r}", day, font=F_HEAD)
            for si, s in enumerate(slots):
                mc, cc = L(2 + 2 * si), L(3 + 2 * si)
                v = rnd.choice(bytype[s]) if w <= 2 else None
                put(ws, f"{mc}{r}", v, fill=INPUT); dv.add(f"{mc}{r}")
                put(ws, f"{cc}{r}", f'=IF({mc}{r}="","",IFERROR(INDEX(Recipes!$D$5:$D${LAST},MATCH({mc}{r},Recipes!$A$5:$A${LAST},0))*Settings!$B$5,0))', USD)
        put(ws, "A13", "Week total", font=F_HEAD); put(ws, "C13", "=SUM(C5:C11,E5:E11,G5:G11,I5:I11)", USD, KPI, Font(name="Arial", size=14, bold=True, color=A))
        put(ws, "A14", "Budget left", font=F_HEAD); put(ws, "C14", "=Settings!B4-C13", USD, KPI, Font(name="Arial", size=14, bold=True, color=A))
        ws.conditional_formatting.add("C14", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="B42318", bold=True)))
        ws.freeze_panes = "B5"
    # ingredient master
    ings = sorted({i for x in RECIPES for i in x[4].split("|") if i}, key=lambda i: (list(AISLE).index(aisle(i)) if aisle(i) in AISLE else 9, i))
    ig = sheet(wb, "Ingredients", "Ingredient index", "Calculated – how many planned meals use each ingredient, per week", A, [22, 14, 10, 10, 10, 10, 8])
    header(ig, 4, ["Ingredient", "Aisle", "Week 1", "Week 2", "Week 3", "Week 4", "Row #"])
    NI = len(ings) + 30
    for k in range(NI):
        r = 5 + k
        put(ig, f"A{r}", ings[k] if k < len(ings) else None, fill=None if k < len(ings) else INPUT)
        put(ig, f"B{r}", aisle(ings[k]) if k < len(ings) else None, fill=None if k < len(ings) else INPUT)
        for w in range(1, 5):
            # meals in week w whose recipe lists this ingredient in any of the 5 columns
            f = "+".join(f"SUMPRODUCT(COUNTIF('Week {w}'!$B$5:$I$11,Recipes!$A$5:$A${LAST})*(Recipes!{c}$5:{c}${LAST}=$A{r}))" for c in "EFGHI")
            put(ig, f"{L(2 + w)}{r}", f'=IF($A{r}="",0,{f})', "0")
        put(ig, f"G{r}", f'=IF(INDEX(C{r}:F{r},\'Grocery List\'!$B$4)>0,MAX($G$4:G{r - 1})+1,"")' if k else f'=IF(INDEX(C{r}:F{r},\'Grocery List\'!$B$4)>0,1,"")')
    ig["G4"].value = "Row #"
    gl = sheet(wb, "Grocery List", "Grocery list", "Choose the week – the list builds itself, grouped by aisle", A, [28, 16, 14, 10])
    put(gl, "A4", "Week", font=F_HEAD); put(gl, "B4", 1, "0", INPUT)
    dvw = DataValidation(type="list", formula1='"1,2,3,4"'); gl.add_data_validation(dvw); dvw.add("B4")
    put(gl, "C4", '="Items: "&MAX(Ingredients!G5:G%d)' % (4 + NI), font=F_HEAD)
    put(gl, "A5", '="Est. cost of week "&B4&": "&TEXT(INDEX(CHOOSE(B4,\'Week 1\'!C13,\'Week 2\'!C13,\'Week 3\'!C13,\'Week 4\'!C13),1),"$#,##0.00")', font=F_SUB)
    header(gl, 7, ["Item", "Aisle", "Used in (meals)", "Got it"])
    for k in range(NI):
        r = 8 + k
        put(gl, f"A{r}", f'=IFERROR(INDEX(Ingredients!$A$5:$A${4 + NI},MATCH({k + 1},Ingredients!$G$5:$G${4 + NI},0)),"")')
        put(gl, f"B{r}", f'=IFERROR(INDEX(Ingredients!$B$5:$B${4 + NI},MATCH({k + 1},Ingredients!$G$5:$G${4 + NI},0)),"")')
        put(gl, f"C{r}", f'=IFERROR(INDEX(Ingredients!$C$5:$F${4 + NI},MATCH({k + 1},Ingredients!$G$5:$G${4 + NI},0),$B$4),"")', "0")
        put(gl, f"D{r}", None, fill=INPUT)
    gl.conditional_formatting.add(f"A8:C{7 + NI}", FormulaRule(formula=[f'$D8<>""'], font=Font(color="AEAEB2", strike=True)))
    wb.move_sheet("Grocery List", -(len(wb.sheetnames) - 3))
    wb.save(path)


# ---------------------------------------------------------------- 3. Savings goals
def savings(path):
    A = "0A6CDB"; wb = Workbook(); NG, ND = 10, 300
    guide(wb, "Savings Goals Tracker 2026 – Targets, Progress Bars & Monthly Plan",
          "Set up to 10 savings goals, each with its own target amount and target date. Log deposits (and withdrawals) as you go: every goal shows saved so far, % complete with a progress bar, what is left, how much you need to save per month to hit the date, and whether you are on track. A 12-month summary shows how much you saved each month.",
          ["1. Goals tab: type each goal's name, target amount, target date and any amount already saved.",
           "2. Deposits tab: one line per deposit – date, goal (dropdown) and amount (use a minus for a withdrawal).",
           "3. Dashboard: progress bars, monthly amount needed and On track / Behind status update by themselves.",
           "4. Monthly tab: totals per month and a chart of your savings pace."], A,
          ["'Needed per month' = what is left ÷ months until the target date (from today).",
           "Each tab is also included as a .csv file in the download for apps that do not open .xlsx."])
    g = sheet(wb, "Goals", "Your goals", "Type in the blue cells", A, [26, 14, 16, 16])
    header(g, 4, ["Goal", "Target", "Target date", "Already saved"])
    sample = [("Emergency fund", 6000, dt.date(2027, 6, 30), 1500), ("Vacation – Portugal", 2800, dt.date(2027, 5, 1), 400), ("New laptop", 1400, dt.date(2027, 2, 1), 200), ("Car down payment", 5000, dt.date(2027, 12, 31), 0), ("Holiday gifts", 600, dt.date(2026, 12, 15), 150)]
    for i in range(NG):
        r = 5 + i
        for j in range(4): put(g, f"{L(j + 1)}{r}", sample[i][j] if i < len(sample) else None, [None, USD, DATE, USD][j], INPUT)
    d = sheet(wb, "Deposits", "Deposits", "One line per deposit; minus for a withdrawal", A, [14, 26, 14, 30])
    header(d, 4, ["Date", "Goal", "Amount", "Note"])
    dv = DataValidation(type="list", formula1="=Goals!$A$5:$A$14"); d.add_data_validation(dv)
    import random
    rnd = random.Random(3); dep = []
    for mth in range(1, 11):
        for goal in [x[0] for x in sample]:
            if rnd.random() < .6: dep.append((dt.date(2026, mth, rnd.randint(1, 27)), goal, rnd.choice([25, 50, 75, 100, 150, 200])))
    dep.sort()
    for k in range(ND):
        r = 5 + k
        for j in range(4): put(d, f"{L(j + 1)}{r}", dep[k][j] if k < len(dep) and j < 3 else None, [DATE, None, USD, None][j], INPUT)
        dv.add(f"B{r}")
    db = sheet(wb, "Dashboard", "Goal progress", "Calculated from Goals and Deposits", A, [24, 13, 13, 9, 24, 13, 12, 14, 14, 12])
    put(db, "A3", "Today", font=F_HEAD); put(db, "B3", "=TODAY()", DATE)
    header(db, 5, ["Goal", "Target", "Saved", "%", "Progress", "Left", "Months left", "Needed / month", "Your pace / month (last 3 mo)", "Status"])
    for i in range(NG):
        r, gr = 6 + i, 5 + i
        put(db, f"A{r}", f'=IF(Goals!A{gr}="","",Goals!A{gr})')
        put(db, f"B{r}", f'=IF(A{r}="","",Goals!B{gr})', USD)
        put(db, f"C{r}", f'=IF(A{r}="","",Goals!D{gr}+SUMIF(Deposits!$B$5:$B${4 + ND},A{r},Deposits!$C$5:$C${4 + ND}))', USD)
        put(db, f"D{r}", f'=IF(A{r}="","",IF(B{r}>0,MIN(1,C{r}/B{r}),0))', PCT)
        put(db, f"E{r}", f'=IF(A{r}="","",REPT("█",ROUND(D{r}*20,0))&REPT("░",20-ROUND(D{r}*20,0)))', font=Font(name="Arial", size=10, color=A))
        put(db, f"F{r}", f'=IF(A{r}="","",MAX(0,B{r}-C{r}))', USD)
        put(db, f"G{r}", f'=IF(A{r}="","",MAX(0,(YEAR(Goals!C{gr})-YEAR($B$3))*12+MONTH(Goals!C{gr})-MONTH($B$3)))', "0")
        put(db, f"H{r}", f'=IF(A{r}="","",IF(F{r}=0,0,IF(G{r}=0,F{r},F{r}/G{r})))', USD)
        put(db, f"I{r}", f'=IF(A{r}="","",SUMIFS(Deposits!$C$5:$C${4 + ND},Deposits!$B$5:$B${4 + ND},A{r},Deposits!$A$5:$A${4 + ND},">="&EDATE($B$3,-3),Deposits!$A$5:$A${4 + ND},"<="&$B$3)/3)', USD)
        put(db, f"J{r}", f'=IF(A{r}="","",IF(F{r}=0,"Done ✓",IF(G{r}=0,"Due now",IF(I{r}>=H{r},"On track","Behind"))))')
    db.conditional_formatting.add("D6:D15", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=A))
    db.conditional_formatting.add("J6:J15", FormulaRule(formula=['$J6="Behind"'], font=Font(color="B42318", bold=True)))
    db.conditional_formatting.add("J6:J15", FormulaRule(formula=['OR($J6="On track",$J6="Done ✓")'], font=Font(color="1E7B34", bold=True)))
    kpi(db, 17, 1, "TOTAL SAVED", "=SUM(C6:C15)", USD, A); kpi(db, 17, 2, "TOTAL TARGET", "=SUM(B6:B15)", USD, A)
    kpi(db, 17, 3, "OVERALL", "=IF(SUM(B6:B15)=0,0,SUM(C6:C15)/SUM(B6:B15))", PCT, A); kpi(db, 17, 8, "NEEDED / MONTH (ALL)", "=SUM(H6:H15)", USD, A)
    mo = sheet(wb, "Monthly", "Saved per month – 2026", "Calculated from Deposits", A, [12, 14, 16])
    header(mo, 4, ["Month", "Saved", "Running total"])
    for m in range(12):
        r = 5 + m
        put(mo, f"A{r}", dt.date(2026, m + 1, 1), "mmm")
        put(mo, f"B{r}", f'=SUMPRODUCT((Deposits!$A$5:$A${4 + ND}>=A{r})*(Deposits!$A$5:$A${4 + ND}<EDATE(A{r},1))*Deposits!$C$5:$C${4 + ND})', USD)
        put(mo, f"C{r}", f"=SUM(Goals!$D$5:$D$14)+SUM($B$5:B{r})", USD)
    ch = BarChart(); ch.title = "Saved per month"; ch.height, ch.width = 7, 16; ch.legend = None
    ch.add_data(Reference(mo, min_col=2, min_row=4, max_row=16), titles_from_data=True); ch.set_categories(Reference(mo, min_col=1, min_row=5, max_row=16))
    mo.add_chart(ch, "E4")
    wb.move_sheet("Dashboard", -(len(wb.sheetnames) - 2))
    wb.save(path)


# ---------------------------------------------------------------- 4. Weekly task & habit planner
def weekly(path):
    A = "6E3FD1"; wb = Workbook(); NT = 400
    guide(wb, "Weekly Task Planner 2026 – Priorities, Habits & Bill Reminders",
          "One task list for the whole year that sorts itself into weeks: every task gets a priority score from its priority and due date, overdue and due-soon tasks are flagged, and the This Week tab ranks your top open tasks. Add a daily habit tracker with streaks, a bill list that shows the next due date and days left, and a notes line for every week.",
          ["1. Tasks tab: type the task, category, priority (High/Medium/Low) and due date; put an x in Done when finished.",
           "2. This Week: type any date in the blue cell (today by default) – see that week's tasks, done %, and the top 10 open tasks ranked by urgency.",
           "3. Habits: tick x for each habit on each day; current streak and monthly % calculate themselves.",
           "4. Bills: type each bill's due day of month – Next due and Days left update daily; due within 5 days turns red."], A,
          ["Priority score = High 3 / Medium 2 / Low 1, +3 if overdue, +2 if due within 2 days, +1 within 7 days.",
           "Weeks run Monday–Sunday."])
    st = sheet(wb, "Settings", "Lists", "Edit the categories and habits", A, [22, 22])
    header(st, 4, ["Categories", "Habits (up to 6)"])
    for i, (c, h) in enumerate(zip(["Work", "Home", "Health", "Money", "Learning", "Family", "Errands", ""], ["Walk 8k steps", "Read 20 min", "No phone after 10pm", "Drink 2L water", "Stretch", "Journal", "", ""])):
        put(st, f"A{5 + i}", c or None, fill=INPUT); put(st, f"B{5 + i}", h or None, fill=INPUT)
    t = sheet(wb, "Tasks", "Tasks – 2026", "Blue cells are yours; Week, Status and Score calculate", A, [12, 34, 12, 10, 14, 7, 9, 12, 7])
    header(t, 4, ["Added", "Task", "Category", "Priority", "Due", "Done", "Week #", "Status", "Score"])
    dvc = DataValidation(type="list", formula1="=Settings!$A$5:$A$12"); dvp = DataValidation(type="list", formula1='"High,Medium,Low"'); dvd = DataValidation(type="list", formula1='"x"')
    for v in (dvc, dvp, dvd): t.add_data_validation(v)
    base = dt.date(2026, 10, 19)
    sample = [("Send Q4 budget to team", "Work", "High", 2, "x"), ("Book dentist", "Health", "Medium", 4, ""), ("Pay car insurance", "Money", "High", 1, ""), ("Fix kitchen tap", "Home", "Low", 9, ""),
              ("Draft blog post", "Learning", "Medium", 5, "x"), ("Call grandma", "Family", "Medium", 3, "x"), ("Renew passport photos", "Errands", "Low", 12, ""), ("Prepare client deck", "Work", "High", 6, ""),
              ("Cancel unused streaming", "Money", "Medium", 0, ""), ("Clean out garage", "Home", "Low", 13, ""), ("Sign up for 5k", "Health", "Low", 7, "x"), ("Review pull requests", "Work", "Medium", 4, "")]
    for k in range(NT):
        r = 5 + k
        if k < len(sample):
            n, c, p, due, done = sample[k]
            vals = [base, n, c, p, base + dt.timedelta(days=due), done or None]
        else:
            vals = [None] * 6
        for j, v in enumerate(vals): put(t, f"{L(j + 1)}{r}", v, [DATE, None, None, None, DATE, None][j], INPUT)
        dvc.add(f"C{r}"); dvp.add(f"D{r}"); dvd.add(f"F{r}")
        put(t, f"G{r}", f'=IF(B{r}="","",WEEKNUM(IF(E{r}="",A{r},E{r}),2))', "0")
        put(t, f"H{r}", f'=IF(B{r}="","",IF(F{r}="x","Done",IF(E{r}="","Open",IF(E{r}<TODAY(),"Overdue",IF(E{r}-TODAY()<=2,"Due soon","Open")))))')
        put(t, f"I{r}", f'=IF(OR(B{r}="",F{r}="x"),"",IF(D{r}="High",3,IF(D{r}="Medium",2,1))+IF(E{r}="",0,IF(E{r}<TODAY(),3,IF(E{r}-TODAY()<=2,2,IF(E{r}-TODAY()<=7,1,0))))+ROW()/100000)', "0")
    t.conditional_formatting.add(f"H5:H{4 + NT}", FormulaRule(formula=['$H5="Overdue"'], font=Font(color="B42318", bold=True)))
    t.conditional_formatting.add(f"H5:H{4 + NT}", FormulaRule(formula=['$H5="Due soon"'], font=Font(color="9A5B00", bold=True)))
    t.conditional_formatting.add(f"A5:I{4 + NT}", FormulaRule(formula=['$F5="x"'], font=Font(color="AEAEB2", strike=True)))
    t.freeze_panes = "A5"
    w = sheet(wb, "This Week", "This week", "Type any date – the week (Mon–Sun) containing it is shown", A, [8, 36, 12, 10, 14, 12])
    put(w, "A4", "Date", font=F_HEAD); put(w, "B4", "=TODAY()", DATE, INPUT)
    put(w, "C4", '="Week "&WEEKNUM(B4,2)', font=F_HEAD)
    TR = f"Tasks!$G$5:$G${4 + NT}"
    kpi(w, 6, 1, "TASKS", f'=COUNTIF({TR},WEEKNUM(B4,2))', "0", A)
    kpi(w, 6, 2, "DONE", f'=COUNTIFS({TR},WEEKNUM(B4,2),Tasks!$F$5:$F${4 + NT},"x")', "0", A)
    kpi(w, 6, 3, "DONE %", "=IF(A7=0,0,B7/A7)", PCT, A)
    kpi(w, 6, 4, "OVERDUE (ALL)", f'=COUNTIF(Tasks!$H$5:$H${4 + NT},"Overdue")', "0", A)
    put(w, "A10", "Top 10 open tasks (all weeks), most urgent first", font=Font(name="Arial", size=12, bold=True, color=INK))
    header(w, 11, ["#", "Task", "Category", "Priority", "Due", "Status"])
    SC = f"Tasks!$I$5:$I${4 + NT}"
    for k in range(10):
        r = 12 + k
        put(w, f"A{r}", k + 1, "0")
        mt = f"MATCH(LARGE({SC},A{r}),{SC},0)"
        for col, src, fmt in (("B", "B", None), ("C", "C", None), ("D", "D", None), ("E", "E", DATE), ("F", "H", None)):
            put(w, f"{col}{r}", f'=IFERROR(INDEX(Tasks!${src}$5:${src}${4 + NT},{mt}),"")', fmt)
    w.conditional_formatting.add("F12:F21", FormulaRule(formula=['$F12="Overdue"'], font=Font(color="B42318", bold=True)))
    put(w, "A23", "Notes for this week", font=Font(name="Arial", size=12, bold=True, color=INK))
    put(w, "B24", '=IFERROR(INDEX(Notes!$B$5:$B$57,WEEKNUM(B4,2)),"")').alignment = Alignment(wrap_text=True)
    h = sheet(wb, "Habits", "Habits – daily", "Put an x on the days you did it", A, [14] + [12] * 6)
    header(h, 6, ["Date"] + [f"=Settings!B{5 + i}" for i in range(6)])
    put(h, "A3", "Current streak", font=F_HEAD); put(h, "A4", "This month %", font=F_HEAD)
    import random
    rnd = random.Random(5); D0 = dt.date(2026, 1, 1); ND = 365
    today = dt.date(2026, 10, 24)
    for k in range(ND):
        r = 7 + k; day = D0 + dt.timedelta(days=k)
        put(h, f"A{r}", day, "ddd mmm d")
        for j in range(6):
            v = "x" if day <= today and day >= dt.date(2026, 9, 1) and rnd.random() < [.85, .7, .5, .8, .6, .4][j] else None
            put(h, f"{L(2 + j)}{r}", v, fill=INPUT)
    for j in range(6):
        c = L(2 + j); rng = f"{c}$7:{c}${6 + ND}"
        hc = L(9 + j); h.column_dimensions[hc].hidden = True; put(h, f"{hc}6", "streak", font=F_HEAD)
        for k in range(ND):
            r = 7 + k; put(h, f"{hc}{r}", f'=IF({c}{r}="x",{"" if k == 0 else hc + str(r - 1) + "+"}1,0)'.replace("=IF(B7=\"x\",1,0)", "=IF(B7=\"x\",1,0)"))
        put(h, f"{c}3", f'=IFERROR(IF(INDEX({rng},MATCH(TODAY(),$A$7:$A${6 + ND},0))="x",INDEX({hc}$7:{hc}${6 + ND},MATCH(TODAY(),$A$7:$A${6 + ND},0)),IFERROR(INDEX({hc}$7:{hc}${6 + ND},MATCH(TODAY(),$A$7:$A${6 + ND},0)-1),0)),0)', "0")
        put(h, f"{c}4", f'=IFERROR(COUNTIFS({rng},"x",$A$7:$A${6 + ND},">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1),$A$7:$A${6 + ND},"<="&TODAY())/DAY(TODAY()),0)', PCT)
    h.conditional_formatting.add(f"B7:G{6 + ND}", CellIsRule(operator="equal", formula=['"x"'], fill=PatternFill("solid", fgColor="E9E1FA"), font=Font(color=A, bold=True)))
    h.freeze_panes = "B7"
    b = sheet(wb, "Bills", "Bills & due dates", "Type the due day of month – red = due within 5 days", A, [24, 12, 12, 10, 14, 10])
    header(b, 4, ["Bill", "Amount", "Due day", "Autopay", "Next due", "Days left"])
    bills = [("Rent", 1450, 1, "No"), ("Phone", 45, 12, "Yes"), ("Electricity", 90, 26, "No"), ("Internet", 60, 18, "Yes"), ("Car insurance", 118, 28, "No"), ("Gym", 35, 5, "Yes")]
    for k in range(15):
        r = 5 + k
        for j in range(4): put(b, f"{L(j + 1)}{r}", bills[k][j] if k < len(bills) else None, [None, USD, "0", None][j], INPUT)
        put(b, f"E{r}", f'=IF(C{r}="","",IF(DAY(TODAY())<=C{r},DATE(YEAR(TODAY()),MONTH(TODAY()),C{r}),DATE(YEAR(TODAY()),MONTH(TODAY())+1,C{r})))', DATE)
        put(b, f"F{r}", f'=IF(C{r}="","",E{r}-TODAY())', "0")
    b.conditional_formatting.add("A5:F19", FormulaRule(formula=['AND($F5<>"",$F5<=5)'], font=Font(color="B42318", bold=True)))
    put(b, "A21", "Monthly bills total", font=F_HEAD); put(b, "B21", "=SUM(B5:B19)", USD)
    n = sheet(wb, "Notes", "Weekly notes", "One line per week – shown on This Week", A, [10, 90])
    header(n, 4, ["Week", "Notes"])
    for k in range(53):
        put(n, f"A{5 + k}", k + 1, "0"); put(n, f"B{5 + k}", "Focus: client deck. Win: budget sent early." if k == 42 else None, fill=INPUT)
    wb.move_sheet("This Week", -(len(wb.sheetnames) - 2))
    wb.save(path)


if __name__ == "__main__":
    {"debt": debt, "meal": meal, "savings": savings, "weekly": weekly}[sys.argv[1]](sys.argv[2])
    print("OK", sys.argv[2])
