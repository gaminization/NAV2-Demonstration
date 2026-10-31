#!/usr/bin/env bash
# Docker helper.
#   scripts/docker.sh build
#   scripts/docker.sh up [world] [model]        e.g.  up house burger
#   GPU=1 scripts/docker.sh up tb3_world waffle   (NVIDIA GPU)
#   scripts/docker.sh shell                       (new terminal in the running container)
#   scripts/docker.sh exec <command...>           e.g.  exec ros2 run nav2-demo mission_client
#   scripts/docker.sh down
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v docker >/dev/null 2>&1 || { echo "Docker is not installed. See docs/DOCKER.md"; exit 1; }
HOST_UID="$(id -u)"; HOST_GID="$(id -g)"
export HOST_UID HOST_GID
mkdir -p "$ROOT/bags" "$HOME/.nav2_demo"

COMPOSE=(docker compose -f docker-compose.yml)
[[ "${GPU:-0}" == "1" ]] && COMPOSE+=(-f docker-compose.gpu.yml)

allow_x() {   # let the container's (same-uid) user draw windows on your screen, nothing wider
  if command -v xhost >/dev/null 2>&1; then
    xhost "+SI:localuser:$(id -un)" >/dev/null
  else
    echo "xhost not found: install x11-xserver-utils (sudo apt install x11-xserver-utils)"
  fi
}

case "${1:-}" in
  build)
    "${COMPOSE[@]}" build ;;
  up)
    export WORLD="${2:-tb3_world}" TURTLEBOT3_MODEL="${3:-${TURTLEBOT3_MODEL:-waffle}}"
    allow_x
    "${COMPOSE[@]}" up --build ;;
  shell)
    "${COMPOSE[@]}" exec sim bash ;;
  exec)
    shift
    "${COMPOSE[@]}" exec sim bash -ic "$*" ;;
  down)
    "${COMPOSE[@]}" down
    command -v xhost >/dev/null 2>&1 && xhost "-SI:localuser:$(id -un)" >/dev/null || true ;;
  *)
    sed -n '2,9p' "$0"; exit 1 ;;
esac
