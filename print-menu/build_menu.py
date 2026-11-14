"""Build the Spotted Duck print menu (v5: food, drinks, desserts) from Jerry's Google Sheet.

Steps:
  1. In Google Sheets: File > Download > Microsoft Excel (.xlsx)
  2. python build_menu.py Spotted_Duck_Menu_Sheet.xlsx
Writes menu.html and Spotted_Duck_Menu_<date>.pdf next to this script:
page 1 = Menu Front (food), page 2 = Menu Back (drinks), page 3 = Menu Desserts,
each 8.5 x 11. Print only the pages you need (e.g. Pages: 3 for desserts).

Needs: pip install openpyxl playwright && playwright install chromium
"""
import json, sys
from pathlib import Path
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent


def flag(v):
    return v is True or str(v or "").strip().lower() in ("true", "yes", "x")


def price(v):
    if v in (None, ""):
        return ""
    try:
        f = float(v)
        return str(int(f)) if f.is_integer() else str(f)
    except (TypeError, ValueError):
        return str(v).strip()


def rows(ws, n_flags):
    out = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        r = (list(r) + [None] * (4 + n_flags))[: 4 + n_flags]
        sec, name, desc, p = r[:4]
        if not name:
            continue
        out.append([str(sec or "").strip(), str(name).strip(), str(desc or "").strip(), price(p)]
                   + [flag(x) for x in r[4:]])
    return out


def read_sheet(path):
    wb = load_workbook(path, data_only=True)
    front_ws = wb["Menu Front"] if "Menu Front" in wb.sheetnames else wb["Menu"]
    front = rows(front_ws, 3)
    back = rows(wb["Menu Back"], 1) if "Menu Back" in wb.sheetnames else []
    dessert = rows(wb["Menu Desserts"], 3) if "Menu Desserts" in wb.sheetnames else []
    settings = {str(r[0]).strip(): ("" if r[1] is None else str(r[1]).strip())
                for r in wb["Settings"].iter_rows(min_row=2, values_only=True) if r[0]}
    return front, back, dessert, settings


def build_html(front, back, dessert, settings):
    t = (HERE / "template.html").read_text()
    t = t.replace("/*FRONT*/[]", json.dumps(front, ensure_ascii=False, indent=0))
    t = t.replace("/*BACK*/[]", json.dumps(back, ensure_ascii=False, indent=0))
    t = t.replace("/*DESSERT*/[]", json.dumps(dessert, ensure_ascii=False, indent=0))
    t = t.replace("/*SETTINGS*/{}", json.dumps(settings, ensure_ascii=False))
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
        overflow = pg.evaluate("""() => [...document.querySelectorAll('.page')].map(p => {
            const foot = p.querySelector('.foot').getBoundingClientRect();
            const menu = p.querySelector('.menu').getBoundingClientRect();
            return menu.bottom > foot.top + 1; })""")
        pg.emulate_media(media="print")
        pg.pdf(path=str(pdf), width="8.5in", height="11in", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()
    for side, over in zip(("food", "drinks", "desserts"), overflow):
        if over:
            print(f"WARNING: the {side} page is too full; items run into the footer.")
    return pdf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    front, back, dessert, settings = read_sheet(sys.argv[1])
    html = build_html(front, back, dessert, settings)
    pdf = build_pdf(html, settings.get("Menu date code", ""))
    print(f"{len(front)} food, {len(back)} drinks, {len(dessert)} dessert items -> {html.name}, {pdf.name}")
