#!/usr/bin/env bash
# Build the workspace.
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash
cd "$ROOT"
colcon build --symlink-install
echo
echo "Build finished. In every new terminal run:  source scripts/env.sh"
