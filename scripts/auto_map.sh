#!/usr/bin/env bash
# Build a map of a world AUTOMATICALLY (frontier exploration), then install it in the repo.
# Usage: scripts/auto_map.sh <world> [extra launch args...]    e.g.  scripts/auto_map.sh house gpu:=true
# Takes roughly 5 to 20 minutes depending on the world. Stops by itself when no frontiers remain.
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORLD="${1:?usage: scripts/auto_map.sh <world> [launch args...]}"; shift || true
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh" >/dev/null

NAME="$(ros2 run nav2-demo world_info "$WORLD" map_name)"
rm -f "$HOME/.nav2_demo/maps/$NAME.yaml" "$HOME/.nav2_demo/maps/$NAME.pgm"

ros2 launch nav2-demo nav2-demo.launch.py world:="$WORLD" mode:=explore "$@" || true

if [[ -f "$HOME/.nav2_demo/maps/$NAME.yaml" ]]; then
  "$ROOT/scripts/install_map.sh" "$NAME"
  echo "Map ready. Run:  ros2 launch nav2-demo nav2-demo.launch.py world:=$WORLD"
else
  echo "No map was produced. See the log above (is Nav2 active? see docs/EXPLORATION.md)."
  exit 1
fi
