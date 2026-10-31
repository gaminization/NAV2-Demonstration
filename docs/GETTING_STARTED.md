# Getting Started (for complete beginners)

No robotics experience needed. Budget about 45 minutes the first time, mostly downloads.

## Words you will see

| Word | Meaning |
|---|---|
| **ROS 2** | A toolkit of programs that talk to each other to run a robot |
| **Node** | One of those programs |
| **Topic** | A named channel nodes use to share data (e.g. `/scan` carries laser readings) |
| **Gazebo** | A simulator: a virtual world with a virtual robot |
| **RViz** | A viewer that shows what the robot "thinks": map, path, laser |
| **Nav2** | The software that plans routes and drives the robot |
| **Map** | A 2D picture of the walls, used for planning |
| **SLAM** | Building a map while driving around |
| **AMCL** | Figures out where the robot is on the map |
| **Costmap** | The map plus "danger zones" around obstacles |

## 0. What you need

- A PC or laptop with **Ubuntu 22.04** (not 24.04, not Windows, not macOS). Dual boot or a dedicated machine is best. Virtual machines work but Gazebo is slow.
- 16 GB RAM recommended, 20 GB free disk, internet.
- A mouse. Gazebo and RViz are graphical.

Check your version: `lsb_release -a` should say `22.04`.

> **Not on Ubuntu 22.04, or do not want to install ROS?** Skip to [DOCKER.md](DOCKER.md).

## 1. Install ROS 2 Humble

Follow the official guide and install **`ros-humble-desktop`**:
<https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html>

## 2. Get the project and install dependencies

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/gaminization/NAV2-Demonstration.git
cd NAV2-Demonstration
./scripts/install.sh          # installs Nav2, TurtleBot3, Gazebo, etc. (asks for your password)
./scripts/build.sh            # compiles this project (about 1 minute)
```

## 3. Open a terminal and prepare it

**Every new terminal** needs this line first (from inside the project folder):

```bash
source scripts/env.sh
```

Then check everything is fine:

```bash
./scripts/check_system.sh
```

Fix anything marked `[FAIL]`. `[WARN]` lines are optional.

## 4. Run the simulation (easiest world)

```bash
ros2 launch nav2-demo nav2-demo.launch.py world:=tb3_world
```

Two windows open: **Gazebo** (3D world with a small robot) and, about 10 seconds later, **RViz** (2D map). First start can take 1 to 2 minutes.

## 5. Make the robot drive itself

Open a **second terminal**:

```bash
cd NAV2-Demonstration
source scripts/env.sh
ros2 run nav2-demo mission_client
```

The robot visits four points. In RViz you will see the green path and the colourful costmap around obstacles.

Prefer clicking? In RViz: **2D Pose Estimate** (drag on the map where the robot is), then **Nav2 Goal** (drag at the destination).

## 6. Watch it avoid an obstacle

While the mission runs, in a third terminal:

```bash
cd NAV2-Demonstration && source scripts/env.sh
./scripts/spawn_obstacle.sh spawn -1.2 -0.5     # drops a red box
./scripts/spawn_obstacle.sh remove              # removes it
```

## 6b. Try another robot

```bash
ros2 launch nav2-demo nav2-demo.launch.py model:=burger
```
See [ROBOT_MODELS.md](ROBOT_MODELS.md).

## 7. Try a harder world

```bash
ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=slam
```
This starts mapping. Drive with the keyboard in another terminal (`ros2 run turtlebot3_teleop teleop_keyboard`), cover every room, then:

```bash
./scripts/save_map.sh house_map
ros2 launch nav2-demo nav2-demo.launch.py world:=house
```

See [WORLDS.md](WORLDS.md) for all worlds and how to set your own waypoints.

## Stopping

Press **Ctrl+C** in the terminal running `ros2 launch`. If Gazebo hangs: `pkill -f gzserver; pkill -f gzclient`.

## Something went wrong?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
