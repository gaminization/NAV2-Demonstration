#!/usr/bin/env bash
# Download the AWS RoboMaker house and warehouse worlds into ~/.nav2_demo/aws
set -euo pipefail
DEST="$HOME/.nav2_demo/aws"
mkdir -p "$DEST"
cd "$DEST"
for repo in aws-robomaker-small-house-world aws-robomaker-small-warehouse-world; do
  if [[ -d "$repo" ]]; then
    echo "$repo already present"
  else
    git clone --depth 1 -b ros2 "https://github.com/aws-robotics/$repo.git"
  fi
done
echo "Done. Try: ros2 launch nav2-demo nav2-demo.launch.py world:=aws_house"
echo "Spawn pose and waypoints for these worlds are placeholders: see docs/WORLDS.md"
