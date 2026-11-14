# Spotted Duck print menu

Printed food menu for The Spotted Duck (the "v5" design): one 8.5 x 11 page, no background color (it's printed on colored paper), with the Meet Vina QR code in the bottom right.

## How it works

1. Jerry edits the Google Sheet (`Spotted_Duck_Menu_Sheet` in Drive, folder *The Grove Menu Tools*).
   - **Menu** tab: Section (dropdown), Dish Name, Dish Descriptor, Price, and Vegan / Vegetarian / Gluten Free checkboxes. Dishes print in row order.
   - **Settings** tab: the date code and the note printed at the bottom.
2. Download the sheet: **File > Download > Microsoft Excel (.xlsx)**.
3. Build the menu:

   ```bash
   pip install openpyxl playwright
   playwright install chromium
   python build_menu.py Spotted_Duck_Menu_Sheet.xlsx
   ```

   This writes `menu.html` and `Spotted_Duck_Menu_<date>.pdf`.

## Files

| File | What it is |
|---|---|
| `template.html` | The v5 layout. The script fills in the dishes and footer note. |
| `build_menu.py` | Reads the sheet, fills the template, prints the PDF. |
| `assets/duck-facing-left.png` | Duck mascot in the header. |
| `assets/vina-qr.png` | Vina QR code (transparent background). |

The Vina QR code opens `https://menus.cellareye.com/spotted-duck/`. The starter sheet (with the Section dropdown) lives in Drive; after importing a fresh copy, select E2:G81 and use Insert > Checkbox.

## Notes

- Tags: a ticked box prints `vg` (vegan), `v` (vegetarian) or `gf` (gluten free) after the dish name. Vegan replaces vegetarian.
- The page is nearly full at the current type sizes (course labels 10.25 pt, dishes and descriptions 10.4 pt, footer 7.75 pt). If dishes are added, check that the PDF is still one page.
- Fonts load from Google Fonts (Newsreader, IBM Plex Mono, Jost), so building needs internet access.
