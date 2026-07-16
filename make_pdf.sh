#!/usr/bin/env bash
# Regenerate the page-by-page PDF from index.html (A4 landscape, one section per page).
# Builds a temp "print" HTML where the @media print sizing is applied UNCONDITIONALLY
# (not gated behind the media query), so charts are sized correctly at first paint —
# this avoids relying on the JS 'beforeprint' event, which doesn't fire reliably
# during headless --print-to-pdf and was leaving charts at their on-screen size
# with dead space below them.
# Usage: ./make_pdf.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT="$HERE/AE_Talent_Pool_Dashboard.pdf"
TMP_HTML="$HERE/.print_render.html"

[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME (set CHROME=/path/to/chrome)"; exit 1; }

python3 - "$HERE/index.html" "$TMP_HTML" <<'PY'
import sys, re
src_path, out_path = sys.argv[1], sys.argv[2]
html = open(src_path, encoding="utf-8").read()

marker = "@media print{"
i = html.find(marker)
if i == -1:
    raise SystemExit("Could not find '@media print{' block in index.html")
# brace-match to find the end of the @media print block
depth = 0
j = i + len(marker) - 1  # position of the opening brace
start_body = j + 1
k = j
while True:
    if html[k] == '{':
        depth += 1
    elif html[k] == '}':
        depth -= 1
        if depth == 0:
            break
    k += 1
body = html[start_body:k]

# Insert the print rules as an UNCONDITIONAL stylesheet (applies at first paint,
# no @media gate, no dependency on JS print events) right before </head>.
inject = f"<style>{body}</style>\n</head>"
out = html.replace("</head>", inject, 1)
open(out_path, "w", encoding="utf-8").write(out)
print(f"prepared {out_path} ({len(out)/1024:.0f}KB)")
PY

rm -f "$OUT"
# window width 1077 => .wrap content ≈1025px, matching the A4-landscape print
# content width so the ECharts canvases render 1:1 instead of being scaled.
"$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --virtual-time-budget=20000 --window-size=1077,900 \
  --no-pdf-header-footer --print-to-pdf="$OUT" \
  "file://$TMP_HTML"

rm -f "$TMP_HTML"

python3 - "$OUT" <<'PY'
import re, sys, os
p = sys.argv[1]
d = open(p, 'rb').read()
pat = rb'/Type\s*/Page[^s]'
n = len(re.findall(pat, d))
print("OK  " + os.path.basename(p) + "  pages=" + str(n) + "  size=" + str(round(len(d)/1024)) + "KB")
PY
