# TurtleBot3 Autonomous Navigation with Nav2 in Gazebo

## Task
Set up a TurtleBot3 robot in a Gazebo environment and configure the ROS 2 Navigation2 (Nav2) stack so it navigates autonomously to a goal while avoiding obstacles. Existing packages are used; no custom navigation algorithm is written.

## Environment
- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic
- TurtleBot3 (waffle), Nav2

## 1. Install

```bash
sudo apt update
sudo apt install -y ros-humble-desktop ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-turtlebot3 ros-humble-turtlebot3-simulations \
  ros-humble-turtlebot3-navigation2
```

## 2. Set environment

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
source ~/.bashrc
```

## 3. Run

**Terminal 1: Gazebo simulation**
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminal 2: Nav2 and RViz**
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  map:=/opt/ros/humble/share/turtlebot3_navigation2/map/map.yaml
```

## 4. Navigate
1. In RViz, click **2D Pose Estimate** and drag on the map where the robot is in Gazebo.
2. Click **Nav2 Goal** and drag at the target location.
3. The robot plans a path and drives to the goal.

## 5. Test obstacle avoidance
1. Send a goal.
2. In Gazebo, use the **Insert** tab to drop a box or cylinder into the robot's path.
3. The obstacle is not in the static map, so the lidar adds it to the local costmap and the robot replans around it.

## How it works
- **AMCL** localizes the robot on the map.
- The **global planner** computes a path to the goal.
- The **local controller** follows the path and steers around obstacles seen by the lidar.
- **Costmaps** inflate obstacles so the robot keeps a safe distance.
