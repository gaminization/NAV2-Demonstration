#!/usr/bin/env bash
# Automated screenshots + video + GIF + rosbag for ONE world.
# Usage: scripts/capture_demo.sh <world> [--no-video]
# Needs an X11 session and: ffmpeg xdotool wmctrl imagemagick x11-utils (scripts/install.sh --capture)
# NOTE: written without access to your machine. Run it once and watch it before trusting it.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORLD="${1:-tb3_world}"
VIDEO=1; [[ "${2:-}" == "--no-video" ]] && VIDEO=0
OUT="$ROOT/media/$WORLD"
OBSTACLE_DELAY="${OBSTACLE_DELAY:-14}"
mkdir -p "$OUT"

for t in ffmpeg xdotool wmctrl import xdpyinfo ros2; do
  command -v "$t" >/dev/null 2>&1 || { echo "Missing '$t'. Run scripts/install.sh --capture"; exit 1; }
done
[[ "${XDG_SESSION_TYPE:-}" == "x11" ]] || { echo "Need an X11 session (log in with 'Ubuntu on Xorg')."; exit 1; }

set +u
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh" >/dev/null
set -u

RES="$(xdpyinfo | awk '/dimensions:/{print $2}')"
W="${RES%x*}"; H="${RES#*x}"
START="$(date +%s)"

# Optional env vars: TURTLEBOT3_MODEL (burger|waffle|waffle_pi), NAV_PROFILE (default|tuned|rpp|mppi),
#                    DYNAMIC=true (moving obstacles)
setsid ros2 launch nav2-demo nav2-demo.launch.py world:="$WORLD" record:=true gpu:=true \
  nav_profile:="${NAV_PROFILE:-default}" dynamic_obstacles:="${DYNAMIC:-false}" > "$OUT/launch.log" 2>&1 &
LAUNCH_PID=$!
FFMPEG_PID=""

cleanup() {
  [[ -n "$FFMPEG_PID" ]] && kill -INT "$FFMPEG_PID" 2>/dev/null
  kill -INT -- "-$LAUNCH_PID" 2>/dev/null
  sleep 8
  pkill -f gzserver 2>/dev/null; pkill -f gzclient 2>/dev/null
  true
}
trap cleanup EXIT

wait_for() {  # wait_for <description> <timeout_s> <command...>
  local desc="$1" timeout="$2" t=0; shift 2
  until "$@" >/dev/null 2>&1; do
    sleep 2; t=$((t + 2))
    if [[ $t -ge $timeout ]]; then echo "Timed out waiting for: $desc"; return 1; fi
  done
}
nav2_active() { ros2 lifecycle get /bt_navigator 2>/dev/null | grep -qw active; }
server_up()   { ros2 action list 2>/dev/null | grep -q run_mission; }
shot() { import -window root "$OUT/$1.png" && echo "saved $1.png"; }

echo "Waiting for Nav2..."
wait_for "Nav2 active" 240 nav2_active || exit 1
wait_for "mission server" 60 server_up || exit 1

# Side-by-side layout: Gazebo left, RViz right
sleep 5
wmctrl -r "Gazebo" -e "0,0,0,$((W / 2)),$H" || true
wmctrl -r "RViz" -e "0,$((W / 2)),0,$((W / 2)),$H" || true
sleep 3

if [[ $VIDEO -eq 1 ]]; then
  ENC=(-c:v libx264 -preset veryfast -crf 23)
  if ffmpeg -loglevel error -f lavfi -i testsrc=size=640x360:rate=1 -frames:v 1 \
       -c:v h264_nvenc -f null - >/dev/null 2>&1; then
    ENC=(-c:v h264_nvenc -preset p4 -cq 23)
    echo "Using NVIDIA NVENC for video encoding"
  fi
  ffmpeg -y -loglevel error -f x11grab -framerate 30 -video_size "${W}x${H}" \
    -i "${DISPLAY}" "${ENC[@]}" -pix_fmt yuv420p "$OUT/demo.mp4" &
  FFMPEG_PID=$!
  sleep 2
fi

shot 01_world_loaded
ros2 run nav2-demo mission_client --world "$WORLD" > "$OUT/mission.log" 2>&1 &
MISSION_PID=$!
sleep 8; shot 02_mission_started

sleep "$OBSTACLE_DELAY"
read -r OX OY < <(ros2 run nav2-demo world_info "$WORLD" demo_obstacle)
"$ROOT/scripts/spawn_obstacle.sh" spawn "$OX" "$OY" demo_box >> "$OUT/launch.log" 2>&1
sleep 3; shot 03_obstacle_added
sleep 6; shot 04_replanning

wait "$MISSION_PID"; MISSION_RC=$?
sleep 2; shot 05_mission_finished

if [[ -n "$FFMPEG_PID" ]]; then
  kill -INT "$FFMPEG_PID" 2>/dev/null; wait "$FFMPEG_PID" 2>/dev/null; FFMPEG_PID=""
  ffmpeg -y -loglevel error -i "$OUT/demo.mp4" \
    -vf "fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" \
    "$OUT/demo.gif" && echo "saved demo.gif"
fi

{
  echo "world=$WORLD"
  echo "mission_exit_code=$MISSION_RC"
  echo "duration_s=$(( $(date +%s) - START ))"
  echo "mission_log:"; cat "$OUT/mission.log"
} > "$OUT/result.txt"
echo "Done. Results in $OUT (mission exit code $MISSION_RC)"
exit "$MISSION_RC"
