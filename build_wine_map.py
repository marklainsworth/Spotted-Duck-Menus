#!/usr/bin/env python3
"""
build_wine_map.py  -  Spotted Duck digital wine menu

WHAT THIS DOES
  Reads the tasting-note data file and rewrites the `const WINE = {...}`
  block inside the menu HTML so the per-wine tasting notes and the
  four-axis card graphic come straight from the spreadsheet. The menu
  stays fully self-contained (no live data fetch), so it keeps working
  on the kiosk and over GitHub Pages.

HOW TO USE
  1. Edit the data file:        data/wine_tasting_notes.csv
  2. Run this from the repo:    python3 build_wine_map.py
  3. Re-upload to GitHub:       SD_winelist_v1.0.html
     (and commit the updated data/wine_tasting_notes.csv)

  Run it from the folder that contains BOTH SD_winelist_v1.0.html and the
  data/ subfolder. It edits the HTML in place and is safe to run repeatedly.

WHICH WINES GET NOTES
  Only rows whose status is 'sourced' or 'estimate' AND that have a
  tasting note are written into the menu. Anything else (a wine you have
  not finished yet, or non-wine items like cocktails) falls back to the
  built-in style logic automatically.

FILES
  Input :  data/wine_tasting_notes.csv
  Output:  SD_winelist_v1.0.html   (the WINE block is replaced in place)
"""

import csv
import json
import os
import re
import sys
import html

# ---- File locations (relative to where you run the script) ----------------
HTML_PATH = "SD_winelist_v1.0.html"
CSV_PATH  = os.path.join("data", "wine_tasting_notes.csv")

# Markers that wrap the generated block in the HTML. Do not hand-edit between
# them; this script overwrites everything inside.
START = "        // === GENERATED WINE MAP START - do not hand-edit; edit data/wine_tasting_notes.csv then run build_wine_map.py ==="
END   = "        // === GENERATED WINE MAP END ==="


def norm(s):
    """Normalize a wine name so the build-time key matches the menu's
    runtime lookup (wineNorm in the HTML): straighten curly quotes,
    lowercase, and collapse whitespace."""
    s = html.unescape(s or "")
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
           .replace("\u201c", '"').replace("\u201d", '"'))
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def truthy(v):
    return str(v).strip().lower() in ("true", "1", "yes", "y")


def main():
    if not os.path.exists(CSV_PATH):
        sys.exit("ERROR: cannot find %s. Run this from the folder that holds "
                 "SD_winelist_v1.0.html and the data/ subfolder." % CSV_PATH)
    if not os.path.exists(HTML_PATH):
        sys.exit("ERROR: cannot find %s in the current folder." % HTML_PATH)

    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))

    wine = {}
    dupes = []
    for r in rows:
        if r.get("status") not in ("sourced", "estimate"):
            continue
        note = (r.get("tasting_note") or "").strip()
        if not note:
            continue
        key = norm(r["display_name"])
        if key in wine:
            dupes.append(key)
        try:
            wine[key] = {
                "body":   int(r["body"]),
                "sweet":  int(r["sweetness"]),
                "acid":   int(r["acidity"]),
                "fourth": int(r["fourth"]),
                "isRed":  truthy(r["is_red"]),
                "note":   note,
            }
        except (ValueError, KeyError) as e:
            sys.exit("ERROR on %r: %s" % (r.get("display_name"), e))

    # Strict JSON, sorted for stable diffs. JSON true/false is valid JS.
    body_json = json.dumps(wine, ensure_ascii=False, indent=0, sort_keys=True)
    block = (
        START + "\n"
        "        // Source of truth: data/wine_tasting_notes.csv. Keyed by the\n"
        "        // normalized wine display name (see wineNorm). This OVERRIDES\n"
        "        // the regex style logic whenever a wine matches.\n"
        "        const WINE = " + body_json + ";\n"
        + END
    )

    src = open(HTML_PATH, encoding="utf-8").read()

    if START in src and END in src:
        pre  = src[:src.index(START)]
        post = src[src.index(END) + len(END):]
        out = pre + block + post
        action = "replaced"
    else:
        # First run: insert the block just before the tasting helpers.
        helper_anchor = "        // Sourced tasting data lookup."
        fn_anchor     = "        function tastingProfile(text, group) {"
        target = helper_anchor if helper_anchor in src else fn_anchor
        if target not in src:
            sys.exit("ERROR: could not find an insertion point in the HTML.")
        out = src.replace(target, block + "\n\n" + target, 1)
        action = "inserted"

    open(HTML_PATH, "w", encoding="utf-8").write(out)

    # Confirm the emitted JSON parses cleanly.
    parsed = json.loads(re.search(r"const WINE = (\{.*?\});", out, re.S).group(1))
    print("%s WINE map: %d wines" % (action, len(parsed)))
    if dupes:
        print("WARNING duplicate keys (last one wins):", ", ".join(dupes))


if __name__ == "__main__":
    main()
