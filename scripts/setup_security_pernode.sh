#!/usr/bin/env bash
# Per-node SROS2 identities (least privilege) for this project's own nodes.
#
# 1) In another terminal start the system UNSECURED so the nodes exist, e.g.:
#       source scripts/env.sh
#       ros2 launch nav2-demo nav2-demo.launch.py dynamic_obstacles:=true
# 2) Run this script (in a terminal with the SAME env: source scripts/env.sh).
# 3) Stop the system, then run it secured:
#       source scripts/env.sh secure
#       ros2 launch nav2-demo nav2-demo.launch.py security:=true security_mode:=pernode
#
# Nodes handled: mission_server dynamic_obstacles explorer (only those running now are done;
# re-run with `mode:=explore` running to add the explorer).
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEYSTORE="${KEYSTORE:-$HOME/.nav2_demo/keystore}"
STATE="$HOME/.nav2_demo"
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh" >/dev/null

"$ROOT/scripts/setup_security.sh" "$KEYSTORE" >/dev/null   # keystore + shared enclave (idempotent)

ALL=/tmp/nav2_demo_policy_all.xml
POLICY="$STATE/policy.xml"
ros2 security generate_policy "$ALL"

MAPPING="$(ros2 run nav2-demo policy_filter "$ALL" "$POLICY" mission_server dynamic_obstacles explorer)"
[[ -n "$MAPPING" ]] || { echo "None of our nodes were running. Start the system first (step 1)."; exit 1; }

: > "$STATE/enclaves.yaml"
while read -r NODE ENCLAVE; do
  [[ -z "$NODE" ]] && continue
  [[ -d "$KEYSTORE/enclaves$ENCLAVE" ]] || ros2 security create_enclave "$KEYSTORE" "$ENCLAVE"
  ros2 security create_permission "$KEYSTORE" "$ENCLAVE" "$POLICY"
  echo "$NODE: $ENCLAVE" >> "$STATE/enclaves.yaml"
  echo "enclave ready: $NODE -> $ENCLAVE"
done <<< "$MAPPING"
chmod -R go-rwx "$KEYSTORE"
echo "Wrote $STATE/enclaves.yaml. Now run with:  security:=true security_mode:=pernode"
