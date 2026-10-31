#!/usr/bin/env bash
# Save the map currently being built by SLAM into the repo and rebuild so launch can find it.
# Usage: scripts/save_map.sh house_map
set -eo pipefail
NAME="${1:?usage: scripts/save_map.sh <map_name>   (e.g. house_map)}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh" >/dev/null
ros2 run nav2_map_server map_saver_cli -f "$ROOT/src/nav2-demo/maps/$NAME" --ros-args -p use_sim_time:=true
"$ROOT/scripts/build.sh"
echo "Saved src/nav2-demo/maps/$NAME.yaml (+ .pgm). Commit both files."
