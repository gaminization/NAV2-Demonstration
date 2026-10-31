#!/usr/bin/env bash
# Copy a map from ~/.nav2_demo/maps into the repo (so you can commit it) and rebuild.
# Usage: scripts/install_map.sh house_map
set -eo pipefail
NAME="${1:?usage: scripts/install_map.sh <map_name>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$HOME/.nav2_demo/maps"
if [[ ! -f "$SRC/$NAME.yaml" && -f "$HOME/.tb3_nav2/maps/$NAME.yaml" ]]; then
  SRC="$HOME/.tb3_nav2/maps"
fi
[[ -f "$SRC/$NAME.yaml" && -f "$SRC/$NAME.pgm" ]] || { echo "Missing $SRC/$NAME.yaml/.pgm"; exit 1; }
cp "$SRC/$NAME.yaml" "$SRC/$NAME.pgm" "$ROOT/src/nav2-demo/maps/"
"$ROOT/scripts/build.sh"
echo "Installed src/nav2-demo/maps/$NAME.* . Commit both files to keep the map."
