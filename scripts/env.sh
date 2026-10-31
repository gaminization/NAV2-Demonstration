#!/usr/bin/env bash
# SOURCE this file in every terminal:   source scripts/env.sh [secure]
# Sets up ROS, the workspace, a private DDS domain and localhost-only networking.
_WS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash
# shellcheck disable=SC1091
[ -f "$_WS_ROOT/install/setup.bash" ] && source "$_WS_ROOT/install/setup.bash"

export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-waffle}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-42}"        # isolates you from other ROS users on the network
export ROS_LOCALHOST_ONLY="${ROS_LOCALHOST_ONLY:-1}" # DDS traffic never leaves this machine

if [ "${1:-}" = "secure" ]; then
  export ROS_SECURITY_KEYSTORE="${ROS_SECURITY_KEYSTORE:-$HOME/.nav2_demo/keystore}"
  export ROS_SECURITY_ENABLE=true
  export ROS_SECURITY_STRATEGY=Enforce
  export ROS_SECURITY_ENCLAVE_OVERRIDE="${ROS_SECURITY_ENCLAVE_OVERRIDE:-/nav2_demo}"
  echo "[nav2-demo] SROS2 enabled (keystore: $ROS_SECURITY_KEYSTORE)"
fi
echo "[nav2-demo] ROS_DOMAIN_ID=$ROS_DOMAIN_ID ROS_LOCALHOST_ONLY=$ROS_LOCALHOST_ONLY MODEL=$TURTLEBOT3_MODEL"
