"""Build The Grove breakfast and lunch menus from the Google Sheet.

Steps:
  1. In Google Sheets: File > Download > Microsoft Excel (.xlsx)
  2. python build_menu.py Grove_Menu_Sheet.xlsx
Writes menu.html and Grove_Menu.pdf (Breakfast, Brunch and Lunch, one legal 8.5 x 14 page each) next to this script.
A tab that is missing from the sheet is skipped.

Needs: pip install openpyxl playwright "qrcode[pil]" && playwright install chromium
Fonts are bundled in assets/fonts, so no internet is needed to build.
"""
import json, sys
from pathlib import Path
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
YES = ("true", "yes", "x")

# Where each section prints. Anything not listed goes to the food column.
PLACE = {
    "Breakfast": {"The 19th Hole": "bar", "Coffee & Tea": "bar", "Juice": "bar", "Soft Drinks": "bar", "Sides": "mid"},
    "Brunch": {"The 19th Hole": "bar", "Wines by the Glass": "bar", "On Tap": "bar", "Cans": "bar",
               "Sides": "mid", "Coffee & Tea": "lower", "Cold Drinks": "lower"},
    "Lunch": {"The 19th Hole": "bar", "Wines by the Glass": "bar", "On Tap": "bar", "Cans": "bar",
              "Desserts": "mid", "Coffee & Tea": "lower", "Cold Drinks": "lower"},
}
MEALS = ("Breakfast", "Brunch", "Lunch")
CORNER = {"Breakfast": "order", "Brunch": "lower", "Lunch": "lower"}
VINA = {"Brunch", "Lunch"}


def flag(v):
    return v is True or str(v or "").strip().lower() in YES


def money(v):
    if v in (None, ""):
        return ""
    try:
        f = float(v)
    except ValueError:
        return str(v).strip()
    return str(int(f)) if f.is_integer() else f"{f:.2f}"


def read_sheet(path):
    wb = load_workbook(path, data_only=True)
    st = {str(r[0]).strip(): ("" if r[1] is None else str(r[1]).strip())
          for r in wb["Settings"].iter_rows(min_row=2, values_only=True) if r[0]}
    pages = []
    for meal in [m for m in MEALS if m in wb.sheetnames]:
        p = {"meal": meal, "when": st.get(f"{meal} hours", ""), "corner": CORNER[meal],
             "food": [], "bar": [], "mid": [], "lower": []}
        for r in wb[meal].iter_rows(min_row=2, values_only=True):
            sec, name, desc, price, vg, v, gf = (list(r) + [None] * 7)[:7]
            if not name or not sec:
                continue
            row = [str(sec).strip(), str(name).strip(), str(desc or "").strip(), money(price),
                   flag(vg), flag(v), flag(gf)]
            p[PLACE[meal].get(row[0], "food")].append(row)
        note = st.get("19th Hole note", "")
        if note:
            at = next((i for i, r in enumerate(p["bar"]) if r[0] == "The 19th Hole"), None)
            if at is not None:
                p["bar"].insert(at, ["The 19th Hole", "", note, ""])
        p["midInline"] = meal != "Lunch"
        p["vina"] = meal in VINA
        pages.append(p)
    return pages, st


def qr_image(url, name="order-qr.png"):
    import qrcode
    qrcode.make(url, border=1).save(HERE / "assets" / name)
    return f"assets/{name}"


PAGES_BUILT = []


def build_html(pages, st):
    PAGES_BUILT[:] = pages
    t = (HERE / "template.html").read_text()
    head, rest = t.split("const PAGES = /*PAGES*/", 1)
    rest = rest[rest.index("\n];") + 3:]
    t = head + "const PAGES = /*PAGES*/" + json.dumps(pages, ensure_ascii=False, indent=0) + ";" + rest
    link = st.get("Course ordering link", "")
    if link:
        t = t.replace('const ORDER_QR = /*ORDER_QR*/"";', f"const ORDER_QR = /*ORDER_QR*/{json.dumps(qr_image(link))};")
    i = t.index("const SETTINGS = /*SETTINGS*/")
    j = t.index("};", i) + 2
    vina = st.get("Vina link", "")
    if vina:
        t = t.replace('const VINA_QR = /*VINA_QR*/"";', f"const VINA_QR = /*VINA_QR*/{json.dumps(qr_image(vina, 'vina-qr.png'))};")
    settings = json.loads(t[i + len("const SETTINGS = /*SETTINGS*/"):j - 1])  # template defaults
    for key, label in (("tagline", "Tagline"), ("disclaimer", "Disclaimer"), ("grab", "Grab-n-Go line"),
                       ("footL", "Footer left"), ("footR", "Footer right")):
        if label in st:
            settings[key] = st[label]
    t = t[:i] + "const SETTINGS = /*SETTINGS*/" + json.dumps(settings, ensure_ascii=False) + ";" + t[j:]
    out = HERE / "menu.html"
    out.write_text(t)
    return out


def build_pdf(html):
    from playwright.sync_api import sync_playwright
    pdf = HERE / "Grove_Menu.pdf"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 1400})
        pg.goto(html.as_uri(), wait_until="networkidle")
        missing = pg.evaluate("""async () => {
            await document.fonts.ready;
            const need = ['600 20pt "Cormorant Garamond"', 'italic 500 13pt "Cormorant Garamond"',
                          '400 9pt Mulish', '700 9pt Mulish', 'italic 400 9pt Mulish'];
            await Promise.all(need.map(f => document.fonts.load(f).catch(() => [])));
            const loaded = new Set([...document.fonts].filter(f => f.status === 'loaded')
                                     .map(f => f.family.replace(/["']/g, '')));
            return ['Cormorant Garamond', 'Mulish'].filter(f => !loaded.has(f));
        }""")
        if missing:
            b.close()
            sys.exit("Fonts did not load (" + ", ".join(missing) + "). "
                     "Make sure grove-print-menu/assets/fonts/ is present; no PDF was made.")
        pg.wait_for_timeout(800)
        over = pg.evaluate("""() => [...document.querySelectorAll('.page')].map(p => {
            const f=p.querySelector('.food'), s=p.querySelector('.side');
            return Math.max(f.scrollHeight-f.clientHeight, s.scrollHeight-s.clientHeight); })""")
        pg.emulate_media(media="print")
        pg.pdf(path=str(pdf), width="8.5in", height="14in", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()
    for meal, o in zip([p["meal"] for p in PAGES_BUILT], over):
        if o > 0:
            print(f"WARNING: the {meal} page is {o}px too long. Shorten descriptions or remove an item.")
    return pdf


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pages, st = read_sheet(sys.argv[1])
    print("Wrote", build_pdf(build_html(pages, st)))
