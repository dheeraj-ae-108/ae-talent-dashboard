#!/usr/bin/env bash
# Regenerate the 2-page "highlights" PDF from slides.html (built by build_slides.py).
# Usage: ./make_slides_pdf.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT="$HERE/AE_Talent_Pool_Highlights_Slides.pdf"

[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME (set CHROME=/path/to/chrome)"; exit 1; }

python3 "$HERE/build_slides.py"

rm -f "$OUT"
"$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --virtual-time-budget=15000 --window-size=1077,800 \
  --no-pdf-header-footer --print-to-pdf="$OUT" \
  "file://$HERE/slides.html"

python3 - "$OUT" <<'PY'
import re, sys, os
p = sys.argv[1]
d = open(p, 'rb').read()
pat = rb'/Type\s*/Page[^s]'
n = len(re.findall(pat, d))
print("OK  " + os.path.basename(p) + "  pages=" + str(n) + "  size=" + str(round(len(d)/1024)) + "KB")
PY
