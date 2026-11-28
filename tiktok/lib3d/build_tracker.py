#!/usr/bin/env python3
"""Builds TikTok_Video_Tracker.xlsx: Videos (one row per video, inputs + KPI formulas), Dashboard, Daily Log, How to use."""
import os, sys, io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from videos_meta import V

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IMG = os.path.join(ROOT, "live_studio", "img")
OUT = os.path.join(ROOT, "TikTok_Video_Tracker.xlsx")
F = "Arial"
H_FILL = PatternFill("solid", fgColor="1F1A2E"); H_FONT = Font(name=F, bold=True, color="FFFFFF", size=10)
IN_FILL = PatternFill("solid", fgColor="FFF7CC")       # cells you fill in
SEC_FILL = PatternFill("solid", fgColor="EEEAF5")
BLUE = Font(name=F, color="0000FF", size=10); BLACK = Font(name=F, color="000000", size=10)
thin = Side(style="thin", color="D9D4E3"); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top"); CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

wb = Workbook()
ws = wb.active; ws.title = "Videos"
N = len(V); R0 = 3; R1 = R0 + N - 1          # data rows

# ---- header groups (row 1) + headers (row 2)
groups = [("A", "F", "VIDEO"), ("G", "H", "POST TEXT"), ("I", "M", "PRODUCT & POSTING  (fill in)"),
          ("N", "V", "STATS FROM TIKTOK  (fill in)"), ("W", "AB", "AUTOMATIC KPIs"), ("AC", "AC", "NOTES")]
cols = [("A", "Preview", 11), ("B", "Nr", 5), ("C", "Video file", 26), ("D", "Product", 22), ("E", "Category", 16), ("F", "Title", 26),
        ("G", "Description (without hashtags)", 60), ("H", "Hashtags", 34),
        ("I", "Price (€)", 9), ("J", "Commission %", 10), ("K", "Status", 11), ("L", "Post date", 11), ("M", "TikTok link", 22),
        ("N", "Views", 10), ("O", "Likes", 9), ("P", "Comments", 9), ("Q", "Shares", 8), ("R", "Saves", 8), ("S", "Avg watch time (s)", 10),
        ("T", "Product clicks", 9), ("U", "Orders", 8), ("V", "Commission earned (€)", 11),
        ("W", "Engagement rate", 10), ("X", "Click rate (clicks/views)", 11), ("Y", "Conversion (orders/clicks)", 11),
        ("Z", "€ per 1,000 views", 10), ("AA", "Est. commission (€)", 11), ("AB", "Verdict", 12), ("AC", "Notes / what to try next", 34)]
from openpyxl.utils import column_index_from_string as ci, get_column_letter as gl
for a, b, txt in groups:
    ws.merge_cells(f"{a}1:{b}1"); c = ws[f"{a}1"]; c.value = txt
    c.font = Font(name=F, bold=True, color="1F1A2E", size=10); c.fill = SEC_FILL; c.alignment = CENTER
for col, name, w in cols:
    c = ws[f"{col}2"]; c.value = name; c.font = H_FONT; c.fill = H_FILL; c.alignment = CENTER; c.border = BORDER
    ws.column_dimensions[col].width = w
ws.row_dimensions[2].height = 42; ws.freeze_panes = "D3"

dv = DataValidation(type="list", formula1='"Not posted,Posted,Planned"', allow_blank=False); ws.add_data_validation(dv)
dv.add(f"K{R0}:K{R1}")

for i, (path, prod, cat, img, price, title, desc, tags) in enumerate(V):
    r = R0 + i
    ws.row_dimensions[r].height = 62
    num = os.path.basename(path).split("_")[0]
    vals = {"B": int(num), "C": os.path.basename(path), "D": prod, "E": cat, "F": title, "G": desc, "H": tags,
            "I": price, "K": "Not posted"}
    for col, v in vals.items():
        c = ws[f"{col}{r}"]; c.value = v; c.font = BLACK; c.alignment = WRAP; c.border = BORDER
    ws[f"B{r}"].alignment = CENTER
    if prod.startswith("Suprent FANGS"): ws[f"J{r}"] = 0.10; ws[f"J{r}"].comment = Comment("10 % commission – from your Suprent FANGS screenshot.", "Tracker")
    for col in "IJKLMNOPQRSTUV":
        c = ws[f"{col}{r}"]; c.fill = IN_FILL; c.border = BORDER
        c.font = BLUE if col not in "K" else Font(name=F, color="0000FF", size=10, bold=True)
        if col not in "M": c.alignment = CENTER
    ws[f"I{r}"].number_format = '#,##0.00 "€"'; ws[f"J{r}"].number_format = "0%"; ws[f"L{r}"].number_format = "DD.MM.YYYY"
    for col in "NOPQRTU": ws[f"{col}{r}"].number_format = "#,##0"
    ws[f"S{r}"].number_format = "0.0"; ws[f"V{r}"].number_format = '#,##0.00 "€"'
    f = {"W": f'=IF(N{r}>0,(O{r}+P{r}+Q{r}+R{r})/N{r},"")',
         "X": f'=IF(N{r}>0,T{r}/N{r},"")',
         "Y": f'=IF(T{r}>0,U{r}/T{r},"")',
         "Z": f'=IF(N{r}>0,V{r}/N{r}*1000,"")',
         "AA": f'=IF(AND(ISNUMBER(I{r}),ISNUMBER(J{r}),U{r}>0),U{r}*I{r}*J{r},"")',
         "AB": f'=IF(OR(K{r}<>"Posted",N{r}=0),"–",IF(Z{r}>=Dashboard!$C$6,"TOP",IF(Z{r}>=Dashboard!$C$7,"OK","IMPROVE")))'}
    for col, v in f.items():
        c = ws[f"{col}{r}"]; c.value = v; c.font = BLACK; c.alignment = CENTER; c.border = BORDER
    for col in "WXY": ws[f"{col}{r}"].number_format = "0.0%"
    ws[f"Z{r}"].number_format = '#,##0.00 "€"'; ws[f"AA{r}"].number_format = '#,##0.00 "€"'
    ws[f"AC{r}"].border = BORDER; ws[f"AC{r}"].alignment = WRAP; ws[f"AC{r}"].fill = IN_FILL; ws[f"AC{r}"].font = BLUE
    # thumbnail
    p = os.path.join(IMG, img + ".png")
    if os.path.exists(p):
        im = Image.open(p).convert("RGBA"); im.thumbnail((74, 74))
        bg = Image.new("RGBA", (78, 78), (255, 255, 255, 255)); bg.paste(im, ((78 - im.size[0]) // 2, (78 - im.size[1]) // 2), im)
        bio = io.BytesIO(); bg.convert("RGB").save(bio, "PNG"); bio.seek(0)
        xi = XLImage(bio); xi.width = 74; xi.height = 74; ws.add_image(xi, f"A{r}")
    ws[f"A{r}"].border = BORDER

# conditional formats
rng = f"AB{R0}:AB{R1}"
ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"TOP"'], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(name=F, bold=True, color="006100")))
ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"OK"'], fill=PatternFill("solid", fgColor="FFEB9C"), font=Font(name=F, bold=True, color="9C5700")))
ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"IMPROVE"'], fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(name=F, bold=True, color="9C0006")))
ws.conditional_formatting.add(f"K{R0}:K{R1}", CellIsRule(operator="equal", formula=['"Posted"'], fill=PatternFill("solid", fgColor="C6EFCE")))
ws.auto_filter.ref = f"B2:AC{R1}"

# ---- Dashboard
d = wb.create_sheet("Dashboard", 0)
d.column_dimensions["A"].width = 2
for col, w in zip("BCDEFGH", (34, 16, 4, 30, 16, 16, 16)): d.column_dimensions[col].width = w
d["B2"] = "TikTok Shop – Video Performance"; d["B2"].font = Font(name=F, bold=True, size=18, color="1F1A2E")
d["B3"] = "Fill in the yellow cells on the Videos sheet. Everything on this page updates by itself."; d["B3"].font = Font(name=F, italic=True, size=10, color="6B6480")
d["B5"] = "SETTINGS"; d["B5"].font = Font(name=F, bold=True, size=10, color="6B6480")
d["B6"] = "Verdict TOP if € per 1,000 views ≥"; d["C6"] = 5
d["B7"] = "Verdict OK if € per 1,000 views ≥"; d["C7"] = 1
for c in ("C6", "C7"):
    d[c].font = BLUE; d[c].fill = PatternFill("solid", fgColor="FFFF00"); d[c].number_format = '#,##0.00 "€"'; d[c].border = BORDER
d["C6"].comment = Comment("Assumption: start values. Change them once you know your own typical earnings per 1,000 views.", "Tracker")
V_ = f"Videos!$%s${R0}:$%s${R1}"
col = lambda c: V_ % (c, c)
kpis = [("Videos total", f"=COUNTA({col('C')})", "0"),
        ("Posted", f'=COUNTIF({col("K")},"Posted")', "0"),
        ("Not posted yet", f'=COUNTIF({col("K")},"Not posted")', "0"),
        ("Total views", f"=SUM({col('N')})", "#,##0"),
        ("Total likes + comments + shares + saves", f"=SUM({col('O')})+SUM({col('P')})+SUM({col('Q')})+SUM({col('R')})", "#,##0"),
        ("Total product clicks", f"=SUM({col('T')})", "#,##0"),
        ("Total orders", f"=SUM({col('U')})", "#,##0"),
        ("Total commission earned", f"=SUM({col('V')})", '#,##0.00 "€"'),
        ("Average € per 1,000 views", f'=IF(SUM({col("N")})>0,SUM({col("V")})/SUM({col("N")})*1000,"")', '#,##0.00 "€"'),
        ("Average click rate", f'=IF(SUM({col("N")})>0,SUM({col("T")})/SUM({col("N")}),"")', "0.00%"),
        ("Average conversion (orders/clicks)", f'=IF(SUM({col("T")})>0,SUM({col("U")})/SUM({col("T")}),"")', "0.0%")]
d["B9"] = "OVERVIEW"; d["B9"].font = Font(name=F, bold=True, size=10, color="6B6480")
for i, (lab, fml, fmt) in enumerate(kpis):
    r = 10 + i
    d[f"B{r}"] = lab; d[f"B{r}"].font = BLACK; d[f"B{r}"].border = BORDER
    d[f"C{r}"] = fml; d[f"C{r}"].font = Font(name=F, bold=True, size=11); d[f"C{r}"].number_format = fmt; d[f"C{r}"].border = BORDER; d[f"C{r}"].alignment = Alignment(horizontal="right")
# best / worst
d["E9"] = "WINNERS & LOSERS"; d["E9"].font = Font(name=F, bold=True, size=10, color="6B6480")
bw = [("Most commission", f'=IF(MAX({col("V")})>0,INDEX({col("D")},MATCH(MAX({col("V")}),{col("V")},0)),"–")', f'=IF(MAX({col("V")})>0,MAX({col("V")}),"")', '#,##0.00 "€"'),
      ("Most views", f'=IF(MAX({col("N")})>0,INDEX({col("D")},MATCH(MAX({col("N")}),{col("N")},0)),"–")', f'=IF(MAX({col("N")})>0,MAX({col("N")}),"")', "#,##0"),
      ("Best € per 1,000 views", f'=IF(COUNT({col("Z")})>0,INDEX({col("D")},MATCH(MAX({col("Z")}),{col("Z")},0)),"–")', f'=IF(COUNT({col("Z")})>0,MAX({col("Z")}),"")', '#,##0.00 "€"'),
      ("Weakest € per 1,000 views (posted)", f'=IF(COUNT({col("Z")})>0,INDEX({col("D")},MATCH(MIN({col("Z")}),{col("Z")},0)),"–")', f'=IF(COUNT({col("Z")})>0,MIN({col("Z")}),"")', '#,##0.00 "€"'),
      ("Best click rate", f'=IF(COUNT({col("X")})>0,INDEX({col("D")},MATCH(MAX({col("X")}),{col("X")},0)),"–")', f'=IF(COUNT({col("X")})>0,MAX({col("X")}),"")', "0.00%"),
      ("Videos to improve", f'=COUNTIF({col("AB")},"IMPROVE")', None, None)]
for i, (lab, name_f, val_f, fmt) in enumerate(bw):
    r = 10 + i
    d[f"E{r}"] = lab; d[f"E{r}"].font = BLACK; d[f"E{r}"].border = BORDER
    d[f"F{r}"] = name_f; d[f"F{r}"].font = Font(name=F, bold=True, size=10); d[f"F{r}"].border = BORDER; d[f"F{r}"].alignment = WRAP
    if val_f: d[f"G{r}"] = val_f; d[f"G{r}"].number_format = fmt; d[f"G{r}"].font = BLACK; d[f"G{r}"].border = BORDER
# per category
cats = sorted(set(v[2] for v in V))
r0 = 24
d[f"B{r0 - 1}"] = "BY CATEGORY"; d[f"B{r0 - 1}"].font = Font(name=F, bold=True, size=10, color="6B6480")
for j, h in enumerate(["Category", "Videos", "", "Posted", "Views", "Commission (€)", "€ per 1,000 views"]):
    if not h: continue
    c = d.cell(row=r0, column=2 + j, value=h); c.font = H_FONT; c.fill = H_FILL; c.alignment = CENTER; c.border = BORDER
for i, cat in enumerate(cats):
    r = r0 + 1 + i
    d[f"B{r}"] = cat
    d[f"C{r}"] = f'=COUNTIF({col("E")},B{r})'
    d[f"E{r}"] = f'=COUNTIFS({col("E")},B{r},{col("K")},"Posted")'
    d[f"F{r}"] = f'=SUMIFS({col("N")},{col("E")},B{r})'
    d[f"G{r}"] = f'=SUMIFS({col("V")},{col("E")},B{r})'
    d[f"H{r}"] = f'=IF(F{r}>0,G{r}/F{r}*1000,"")'
    for cc in "BCEFGH": d[f"{cc}{r}"].border = BORDER; d[f"{cc}{r}"].font = BLACK
    d[f"F{r}"].number_format = "#,##0"; d[f"G{r}"].number_format = '#,##0.00 "€"'; d[f"H{r}"].number_format = '#,##0.00 "€"'
d.column_dimensions["H"].width = 18
rE = r0 + len(cats)
ch = BarChart(); ch.type = "bar"; ch.style = 10; ch.title = "Commission by category (€)"
ch.add_data(Reference(d, min_col=7, min_row=r0, max_row=rE), titles_from_data=True)
ch.set_categories(Reference(d, min_col=2, min_row=r0 + 1, max_row=rE))
ch.height = 8; ch.width = 18; ch.legend = None; ch.roundedCorners = False
ch.x_axis.delete = False; ch.y_axis.delete = False
d.add_chart(ch, f"B{rE + 3}")
# top 5 by commission (helper rank in Videos!AD hidden: commission + tiny row tie-break)
ws["AD2"] = "rank helper"; ws.column_dimensions["AD"].hidden = True
for i in range(N):
    r = R0 + i; ws[f"AD{r}"] = f"=IF(ISNUMBER(V{r}),V{r},0)+ROW()/1000000"
d["E17"] = "TOP 5 BY COMMISSION"; d["E17"].font = Font(name=F, bold=True, size=10, color="6B6480")
for k in range(1, 6):
    r = 17 + k
    d[f"E{r}"] = f'=IF(LARGE({col("AD")},{k})>=0.01,"#{k}  "&INDEX({col("D")},MATCH(LARGE({col("AD")},{k}),{col("AD")},0))&"  (Nr "&INDEX({col("B")},MATCH(LARGE({col("AD")},{k}),{col("AD")},0))&")","#{k}  –")'
    d[f"G{r}"] = f'=IF(LARGE({col("AD")},{k})>=0.01,INDEX({col("V")},MATCH(LARGE({col("AD")},{k}),{col("AD")},0)),"")'
    d[f"G{r}"].number_format = '#,##0.00 "€"'
    for cc in "EG": d[f"{cc}{r}"].font = BLACK; d[f"{cc}{r}"].border = BORDER
    d.merge_cells(f"E{r}:F{r}")

# ---- Daily Log
lg = wb.create_sheet("Daily Log")
heads = [("A", "Date", 12), ("B", "Video Nr", 9), ("C", "Product", 28), ("D", "Views (total)", 12), ("E", "Likes (total)", 12),
         ("F", "Orders (total)", 12), ("G", "Commission (€, total)", 14), ("H", "New views since last entry", 14), ("I", "Note", 40)]
for c_, h, w in heads:
    cell = lg[f"{c_}1"]; cell.value = h; cell.font = H_FONT; cell.fill = H_FILL; cell.alignment = CENTER; cell.border = BORDER; lg.column_dimensions[c_].width = w
lg.row_dimensions[1].height = 32; lg.freeze_panes = "A2"
import datetime
for r in range(2, 202):
    lg[f"C{r}"] = f'=IF(B{r}="","",IFERROR(INDEX({col("D")},MATCH(B{r},{col("B")},0)),"?"))'
    lg[f"H{r}"] = (f'=IF(OR(B{r}="",D{r}=""),"",IF(COUNTIF($B$1:B{r - 1},B{r})=0,D{r},D{r}-LOOKUP(2,1/($B$1:B{r - 1}=B{r}),$D$1:D{r - 1})))' if r > 2 else f'=IF(OR(B{r}="",D{r}=""),"",D{r})')
    for c_ in "ABDEFGI": lg[f"{c_}{r}"].fill = IN_FILL; lg[f"{c_}{r}"].font = BLUE
    lg[f"A{r}"].number_format = "DD.MM.YYYY"; lg[f"G{r}"].number_format = '#,##0.00 "€"'
    for c_ in "DEFH": lg[f"{c_}{r}"].number_format = "#,##0"
lg["A2"] = datetime.date(2026, 11, 29); lg["B2"] = 10; lg["D2"] = 1250; lg["E2"] = 84; lg["F2"] = 1; lg["G2"] = 17.00
lg["I2"] = "EXAMPLE ROW – overwrite or delete it. One row per video per day you check."
lg["I2"].font = Font(name=F, italic=True, color="9C0006", size=10)

# ---- How to use
hw = wb.create_sheet("How to use")
hw.column_dimensions["A"].width = 110
lines = [("How to use this tracker", True),
         ("1. Videos sheet: one row per video. Left: preview + file name. Middle: title, description and hashtags to copy into TikTok.", False),
         ("2. When you post a video: set Status to 'Posted', enter the post date and paste the TikTok link.", False),
         ("3. Every few days, copy the numbers from TikTok Studio (views, likes, comments, shares, saves, avg watch time) and from", False),
         ("   TikTok Shop Affiliate Center (product clicks, orders, commission earned) into the yellow cells.", False),
         ("4. Columns W–AB calculate themselves: engagement, click rate, conversion, € per 1,000 views and a verdict (TOP / OK / IMPROVE).", False),
         ("5. Dashboard: totals, best and weakest videos, top 5 by commission and results per category.", False),
         ("6. Daily Log (optional): write the total numbers per video per day to see how fast each video grows.", False),
         ("", False),
         ("Colours: yellow cells with blue text = you type here. Black text = formulas, don't type over them.", False),
         ("Commission %: enter it per product from the Affiliate Center (e.g. 10 % for Suprent FANGS) to get an estimated commission.", False),
         ("Verdict thresholds: change them on the Dashboard (Settings).", False),
         ("", False),
         ("How to read the verdict", True),
         ("TOP: earns well per view – make more videos like this (same hook, same product type, post at the same time of day).", False),
         ("OK: works – test a stronger first 2 seconds or a clearer price in the hook.", False),
         ("IMPROVE: many views but few clicks → hook or product doesn't match the audience; few views → change hook/thumbnail/time.", False),
         ("High views + low click rate → the video entertains but doesn't sell: show product and price earlier.", False),
         ("High click rate + low conversion → price or product page is the problem, not the video.", False)]
for i, (t, b) in enumerate(lines):
    c = hw.cell(row=1 + i, column=1, value=t); c.font = Font(name=F, bold=b, size=12 if b else 10)

wb.move_sheet("Videos", offset=-0)
wb.active = 0
wb.save(OUT); print("->", OUT, N, "videos")
