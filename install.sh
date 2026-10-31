#!/usr/bin/env bash
# Installs requirements, configures the environment, and builds the workspace.
# Target: Ubuntu 22.04 + ROS 2 Humble (https://docs.ros.org/en/humble/Installation.html)
set -e

if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "ROS 2 Humble not found at /opt/ros/humble."
  echo "Install it first: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html"
  exit 1
fi

sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-turtlebot3 ros-humble-turtlebot3-simulations \
  ros-humble-turtlebot3-navigation2 \
  ros-humble-slam-toolbox \
  python3-colcon-common-extensions

# Environment (added once)
if ! grep -q "# nav2-demo" ~/.bashrc; then
  cat >> ~/.bashrc <<'EOB'

# nav2-demo
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
EOB
fi

# Build the workspace
source /opt/ros/humble/setup.bash
cd "$(dirname "$0")"
colcon build --symlink-install

echo
echo "Install complete. Now run:"
echo "  source ~/.bashrc && source install/setup.bash"
echo "  ros2 launch nav2-demo nav2-demo.launch.py"
