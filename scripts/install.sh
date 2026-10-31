#!/usr/bin/env bash
# Install all dependencies (Ubuntu 22.04 + ROS 2 Humble).
# Usage: scripts/install.sh [--capture]    (--capture adds screenshot/video tools)
set -euo pipefail
CAPTURE=0
[[ "${1:-}" == "--capture" ]] && CAPTURE=1

# shellcheck disable=SC1091
. /etc/os-release
if [[ "$VERSION_ID" != "22.04" ]]; then
  echo "This project targets Ubuntu 22.04 (ROS 2 Humble). You have $VERSION_ID."
  exit 1
fi
if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble is not installed. Follow the official guide first:"
  echo "  https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html"
  echo "Install 'ros-humble-desktop', then re-run this script."
  exit 1
fi

PKGS=(
  ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-nav2-simple-commander
  ros-humble-turtlebot3 ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-navigation2
  ros-humble-turtlebot3-cartographer ros-humble-turtlebot3-teleop ros-humble-turtlebot3-msgs
  ros-humble-gazebo-ros-pkgs ros-humble-cartographer ros-humble-cartographer-ros
  ros-humble-rosbag2 ros-humble-rosbag2-storage-mcap ros-humble-sros2
  python3-colcon-common-extensions python3-yaml git mesa-utils
)
if [[ $CAPTURE -eq 1 ]]; then
  PKGS+=(ffmpeg xdotool wmctrl imagemagick x11-utils scrot)
fi

sudo apt update
sudo apt install -y "${PKGS[@]}"
# Optional Nav2 plugins used by nav_profile:=rpp / mppi / smac planner. Failure is not fatal.
sudo apt install -y ros-humble-nav2-regulated-pure-pursuit-controller ros-humble-nav2-smac-planner \
  || echo "Note: RPP/Smac packages not installed; nav_profile:=rpp will not work."
sudo apt install -y ros-humble-nav2-mppi-controller \
  || echo "Note: MPPI controller not available; nav_profile:=mppi will not work."
echo "Dependencies installed. Next: scripts/build.sh"
