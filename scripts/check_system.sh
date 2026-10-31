#!/usr/bin/env bash
# Environment doctor: tells you what is missing before you waste time.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
ok()   { echo "[ OK ] $*"; }
warn() { echo "[WARN] $*"; }
fail() { echo "[FAIL] $*"; FAILED=1; }

# shellcheck disable=SC1091
. /etc/os-release
[[ "$VERSION_ID" == "22.04" ]] && ok "Ubuntu 22.04" || fail "Ubuntu is $VERSION_ID (need 22.04)"
[[ -f /opt/ros/humble/setup.bash ]] && ok "ROS 2 Humble installed" || fail "ROS 2 Humble missing"

for p in navigation2 nav2-bringup nav2-simple-commander turtlebot3-gazebo turtlebot3-navigation2 \
         turtlebot3-cartographer gazebo-ros-pkgs rosbag2 sros2; do
  dpkg -s "ros-humble-$p" >/dev/null 2>&1 && ok "ros-humble-$p" || fail "ros-humble-$p missing (scripts/install.sh)"
done
[[ -f "$ROOT/install/setup.bash" ]] && ok "workspace built" || fail "workspace not built (scripts/build.sh)"

if command -v nvidia-smi >/dev/null 2>&1; then
  ok "NVIDIA: $(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -1)"
else
  warn "nvidia-smi not found: NVIDIA driver not installed (software/Intel rendering will be used)"
fi
[[ "${XDG_SESSION_TYPE:-}" == "x11" ]] && ok "X11 session" || warn "Session is '${XDG_SESSION_TYPE:-unknown}'. Screen capture scripts need X11 ('Ubuntu on Xorg' at login)"
for t in ffmpeg xdotool wmctrl import xdpyinfo; do
  command -v "$t" >/dev/null 2>&1 && ok "capture tool: $t" || warn "capture tool missing: $t (scripts/install.sh --capture)"
done
command -v docker >/dev/null 2>&1 && ok "docker available (optional, see docs/DOCKER.md)" || warn "docker not installed (optional)"
exit $FAILED
