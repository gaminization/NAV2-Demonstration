#!/usr/bin/env bash
# Builds the workspace on first start, then runs the requested command.
set -e
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash
cd /ws
if [ ! -f install/setup.bash ]; then
  echo "[docker] First start: building workspace (about 1 minute)..."
  colcon build --symlink-install
fi
# shellcheck disable=SC1091
source install/setup.bash
exec "$@"
