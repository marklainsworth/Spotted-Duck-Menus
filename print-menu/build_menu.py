"""Build the Spotted Duck print menu (v5) from Jerry's Google Sheet.

Steps:
  1. In Google Sheets: File > Download > Microsoft Excel (.xlsx)
  2. python build_menu.py Spotted_Duck_Menu_Sheet.xlsx
Writes menu.html and Spotted_Duck_Menu_<date>.pdf (8.5 x 11, one page) next to this script.

Needs: pip install openpyxl playwright && playwright install chromium
"""
import json, re, sys
from pathlib import Path
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
YES = ("true", "yes", "x")

def flag(v):
    return v is True or str(v or "").strip().lower() in YES

def read_sheet(path):
    wb = load_workbook(path, data_only=True)
    rows = []
    for r in wb["Menu"].iter_rows(min_row=2, values_only=True):
        sec, dish, desc, price, vegan, veg, gf = (list(r) + [None] * 7)[:7]
        if not dish:
            continue
        if price in (None, ""):
            p = ""
        else:
            p = str(int(price)) if float(price).is_integer() else str(price)
        rows.append([sec or "", str(dish).strip(), (desc or "").strip(), p,
                     flag(vegan), flag(veg), flag(gf)])
    settings = {r[0]: r[1] for r in wb["Settings"].iter_rows(min_row=2, values_only=True) if r[0]}
    date = str(settings.get("Menu date code", "")).strip()
    foot = f"{str(settings.get('Footer note', '')).strip()} {date}".strip()
    return rows, foot, date

def build_html(rows, foot):
    t = (HERE / "template.html").read_text()
    t = t.replace('/*FOOTNOTE*/""', json.dumps(foot, ensure_ascii=False))
    t = t.replace("/*MENU*/[]", json.dumps(rows, ensure_ascii=False, indent=0))
    out = HERE / "menu.html"
    out.write_text(t)
    return out

def build_pdf(html, date):
    from playwright.sync_api import sync_playwright
    pdf = HERE / f"Spotted_Duck_Menu_{date or 'latest'}.pdf"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 816, "height": 1056})
        pg.goto(html.as_uri(), wait_until="networkidle")
        pg.wait_for_timeout(800)
        pg.add_style_tag(content="@media print{.sheet-wrap{overflow:visible!important;height:auto!important;width:8.5in!important}}")
        pg.emulate_media(media="print")
        pg.pdf(path=str(pdf), width="8.5in", height="11in", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()
    return pdf

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rows, foot, date = read_sheet(sys.argv[1])
    html = build_html(rows, foot)
    pdf = build_pdf(html, date)
    print(f"{len(rows)} dishes -> {html.name}, {pdf.name}")
