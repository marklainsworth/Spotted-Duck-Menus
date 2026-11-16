# The Grove at Point Pinos print menu

Printed menus for The Grove: **Breakfast**, **Brunch** and **Lunch**, one legal (8.5 x 14) page each, in one PDF.

## How it works

1. Jerry edits the Google Sheet `Grove_Menu_Sheet` (Drive folder *The Grove Menu Tools*).
   - **Breakfast**, **Brunch** and **Lunch** tabs: Section (dropdown), Item Name, Description, Price, and Vegan / Vegetarian / Gluten Free checkboxes. Items print in row order inside each section.
   - **Settings** tab: serving hours for each menu, the Grab-n-Go line, the 19th Hole note, footer lines, the course-ordering link, and (optional) a Vina link.
   - **How to Use** tab: which section prints where.
2. Download the sheet: **File > Download > Microsoft Excel (.xlsx)**.
3. Build:

   ```bash
   pip install openpyxl playwright "qrcode[pil]"
   playwright install chromium
   python build_menu.py Grove_Menu_Sheet.xlsx
   ```

   This writes `menu.html` and `Grove_Menu.pdf`, and warns if any page runs long.

## Files

| File | What it is |
|---|---|
| `template.html` | The v6 layout. The script fills in the items, hours and settings. |
| `build_menu.py` | Reads the sheet, fills the template, prints the PDF. |
| `assets/grove-logo.png` | Horizontal Grove logo for the header. |
| `assets/fonts/` | Cormorant Garamond and Mulish, bundled so the build needs no internet. |

## Where sections print

| Menu | Food (left column) | Green drinks panel | Under the drinks | Bottom-right |
|---|---|---|---|---|
| Breakfast | Breakfast | The 19th Hole, Coffee & Tea, Juice, Soft Drinks | Sides | Order-from-the-course QR box |
| Brunch | Brunch Favorites, Midday Plates | The 19th Hole, Wines by the Glass, On Tap, Cans | Sides | Coffee & Tea, Cold Drinks |
| Lunch | Starters & Salads, Sandwiches & Plates | The 19th Hole, Wines by the Glass, On Tap, Cans | Desserts | Coffee & Tea, Cold Drinks |

Brunch and Lunch also carry the Meet Vina™ block at the bottom of the food column.

## Notes

- If every item in a section has the same price, it prints once on the section heading (e.g. Desserts 10).
- Ticked boxes print `vg` / `v` / `gf` after the name (vegan replaces vegetarian); a key appears in the footer when any are used.
- **Course ordering link** blank = "Coming Soon!" in the breakfast QR box; filled = a real QR code. Same for **Vina link** on brunch and lunch.
- Text starting with "TODO" prints in orange as a placeholder, and "New Dish" rows print as written. Clear both before printing.
- A tab that is missing from the sheet is skipped.
