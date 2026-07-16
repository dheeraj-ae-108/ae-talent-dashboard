#!/usr/bin/env bash
# Regenerate the page-by-page PDF from index.html (A4 landscape, one section per page).
# Usage: ./make_pdf.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT="$HERE/AE_Talent_Pool_Dashboard.pdf"

[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME (set CHROME=/path/to/chrome)"; exit 1; }

rm -f "$OUT"
# window width 1077 => .wrap content ≈1025px, which matches the A4-landscape print
# content width — this keeps the ECharts canvases 1:1 instead of scaling them.
"$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --virtual-time-budget=20000 --window-size=1077,800 \
  --no-pdf-header-footer --print-to-pdf="$OUT" \
  "file://$HERE/index.html"

python3 - "$OUT" <<'PY'
import re, sys, os
p = sys.argv[1]
d = open(p, 'rb').read()
print(f"OK  {os.path.basename(p)}  pages={len(re.findall(rb'/Type\s*/Page[^s]', d))}  size={len(d)/1024:.0f}KB")
PY
