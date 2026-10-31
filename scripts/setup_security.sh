#!/usr/bin/env bash
# Create an SROS2 keystore and one enclave shared by all nodes of this project.
# Usage: scripts/setup_security.sh [keystore_dir]
set -eo pipefail
KEYSTORE="${1:-$HOME/.nav2_demo/keystore}"
ENCLAVE="/nav2_demo"
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash

if [[ ! -d "$KEYSTORE" ]]; then
  ros2 security create_keystore "$KEYSTORE"
else
  echo "Keystore already exists: $KEYSTORE"
fi
if [[ ! -d "$KEYSTORE/enclaves$ENCLAVE" ]]; then
  ros2 security create_enclave "$KEYSTORE" "$ENCLAVE"
else
  echo "Enclave already exists: $ENCLAVE"
fi
chmod -R go-rwx "$KEYSTORE"
echo
echo "Done. Use it with either:"
echo "  source scripts/env.sh secure && ros2 launch nav2-demo nav2-demo.launch.py security:=true"
echo "Keep $KEYSTORE private and never commit it."
