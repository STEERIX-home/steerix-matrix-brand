#!/bin/bash
# Rebuild the STEERIX / MATRIX brand kit from the MATRIX web app's brand sources (web/src/brand and
# web/public/brand/startup-intro.svg): logos, animations and their renders, fonts, the brand sheet. Builds into the
# repository root, then copies the kit to the Desktop folder (adds and updates, never deletes there).
# Uses Playwright's cached headless Chromium (one browser at a time) and ffmpeg.
#   tools/build.sh [OUT_DIR]        (default: the repository root)
set -eo pipefail
cd "$(dirname "$0")"
PY=~/office-film-v5/dish/.venv/bin/python      # websockets, fontTools, Pillow
ROOT=$(cd .. && pwd)
OUT=${1:-$ROOT}
DESK=$HOME/바탕화면/STEERIX-MATRIX-로고
mkdir -p tmp check
python3 extract.py ~/matrix_reboot/web geo.json
$PY logos.py "$OUT"
python3 anim.py "$OUT"
python3 pages.py "$OUT"
$PY fonts.py "$OUT"
$PY render.py "$OUT"
$PY sheet.py "$OUT"
if [ "$OUT" = "$ROOT" ]; then
  rsync -a --exclude .git --exclude tools --exclude README.md --exclude .gitignore "$ROOT/" "$DESK/"
  echo "copied to $DESK"
fi
echo "built $OUT"
