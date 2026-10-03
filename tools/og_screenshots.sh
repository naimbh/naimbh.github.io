#!/bin/bash
# Social-share preview images (Facebook, LinkedIn, X, WhatsApp ...) = a real
# screenshot of each site's desktop hero, 1200x630.
# Run after changing either hero:   bash tools/og_screenshots.sh
set -u
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP="$(mktemp -d)"

python3 -m http.server 8791 -d . >/dev/null 2>&1 & MAIN=$!; disown
python3 -m http.server 8792 -d dev >/dev/null 2>&1 & DEV=$!; disown
trap 'kill $MAIN $DEV 2>/dev/null; rm -rf "$TMP"' EXIT
sleep 1

shot() { # url  output.jpg
  # 1720x903 has the same shape as 1200x630; reduced motion = no half-finished animations
  ( perl -e 'alarm 30; exec @ARGV' "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-dark-mode --force-prefers-reduced-motion --window-size=1720,903 --timeout=3000 \
    --user-data-dir="$TMP/profile" --screenshot="$TMP/shot.png" "$1" >/dev/null 2>&1 ) 2>/dev/null
  sips -z 630 1200 -s format jpeg -s formatOptions 86 "$TMP/shot.png" --out "$2" >/dev/null
  echo "saved $2"
}

shot http://localhost:8791/ images/og/naim-bin-hasan-academic-site.jpg
shot http://localhost:8792/ dev/images/naim-bin-hasan-web-developer-site.jpg
