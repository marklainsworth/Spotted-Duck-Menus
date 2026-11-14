# Spotted Duck print menu

The printed v5 menu for The Spotted Duck: three 8.5 x 11 pages in one PDF. Page 1 is food, page 2 is drinks, page 3 is desserts. Print only the pages you need (Pages: 1-2 for the dinner menu, Pages: 3 for desserts). There's no background color because the menu is printed on colored paper. The Meet Vina QR code sits bottom right on every page.

## How it works

1. Jerry edits the Google Sheet (`Spotted_Duck_Menu_Sheet` in Drive, folder *The Grove Menu Tools*).
   - **Menu Front** tab (food): Section (dropdown), Dish Name, Dish Descriptor, Price, and Vegan / Vegetarian / Gluten Free checkboxes.
   - **Menu Back** tab (drinks): Section (dropdown), Drink Name, Drink Descriptor, Price, Non-Alcoholic checkbox.
   - **Menu Desserts** tab: Section (dropdown), Item Name, Item Descriptor, Price, and Vegan / Vegetarian / Gluten Free checkboxes.
   - **Settings** tab: the date code, the front footer note, the back footer note and the back info line (hours, phone, Instagram), and an optional Dessert footer note.
   - Items fill down the left column first, then the next column, in sheet order.
2. Download the sheet: **File > Download > Microsoft Excel (.xlsx)**.
3. Build the menu:

   ```bash
   pip install openpyxl playwright
   playwright install chromium
   python build_menu.py Spotted_Duck_Menu_Sheet.xlsx
   ```

   This writes `menu.html` and `Spotted_Duck_Menu_<date>.pdf` (three pages). If a page is too full, it prints a warning.

## Files

| File | What it is |
|---|---|
| `template.html` | The v5 layout for all three pages. The script fills in the items and notes. |
| `build_menu.py` | Reads the sheet, fills the template, prints the PDF. |
| `assets/duck-facing-left.png` | Duck mascot in the header. |
| `assets/vina-qr.png` | Vina QR code (transparent background). |
| `assets/fonts/` | The three menu fonts and `fonts.css`. |

## Notes

- Food tags: a ticked box prints `vg` (vegan), `v` (vegetarian) or `gf` (gluten free) after the dish name. Vegan replaces vegetarian.
- Drink tags: a ticked Non-Alcoholic box prints `na`.
- When every drink in a section has the same price (the session cocktails, for example), the price prints once next to the section name.
- Type sizes: course labels 10.25 pt, item names and descriptions 10.4 pt, footer 7.75 pt. The food side is nearly full, so check the PDF after adding dishes.
- Fonts (Newsreader, IBM Plex Mono, Jost; SIL Open Font License) are bundled in `assets/fonts/`, so builds look the same everywhere and don't need Google Fonts. If they fail to load, the script stops instead of printing a menu in the wrong font.
