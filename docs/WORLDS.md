# Worlds

Switch worlds with one launch argument:

```bash
ros2 launch nav2-demo nav2-demo.launch.py world:=<name>
```

| `world:=` | Difficulty | Map | Notes |
|---|---|---|---|
| `tb3_world` | easy | ships with Nav2 | 9 pillars in a hexagon. Start here. |
| `house` | medium | build it (5 min) | Rooms, doors, furniture |
| `stage4` | medium | build it | Arena with walls and obstacles (experimental) |
| `aws_house` | hard | ships with the AWS repo | Run `scripts/install_aws_worlds.sh` first (experimental) |
| `aws_warehouse` | hard | ships with the AWS repo | Shelves and narrow aisles (experimental) |

**Honest status:** none of these entries have been run by the author of this file. Spawn positions, waypoints and obstacle positions in `src/nav2-demo/config/worlds.yaml` are placeholders. Verify them (below).

## Your own world file

```bash
ros2 launch nav2-demo nav2-demo.launch.py world_file:=/path/to/my.world map:=/path/to/my_map.yaml x_pose:=0.0 y_pose:=0.0
```
(Waypoints still come from the `world:=` entry. Add your own entry for missions.)

## Adding a world permanently

Copy an entry in `src/nav2-demo/config/worlds.yaml`, give it a new name, set `world_file`, `map`, `spawn`, `initial_pose`, `waypoints`. Then `./scripts/build.sh` (not needed if you built with `--symlink-install`, which `build.sh` does).

## Building a map automatically

```bash
./scripts/auto_map.sh house
```
See [EXPLORATION.md](EXPLORATION.md).

## Building a map by hand

```bash
ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=slam
ros2 run turtlebot3_teleop teleop_keyboard         # second terminal; drive slowly
./scripts/save_map.sh house_map                    # third terminal, when the map looks complete
```
The map origin is where the robot started, so `initial_pose` for self-built maps is `0, 0, 0`.

## Finding real waypoint coordinates

1. Launch the world in `nav` mode.
2. In RViz click **Publish Point** in the toolbar, then click a free spot on the map.
3. In a terminal: `ros2 topic echo /clicked_point` and read `x` and `y`.
4. Put them in `worlds.yaml`. Pick points in the middle of rooms, not near walls.

## Coordinate frames (important)

- `spawn` and `demo_obstacle`: **Gazebo world** frame.
- `initial_pose` and `waypoints`: **map** frame.
These are only equal when the map was made with the robot at the world origin. That is why a SLAM map with a spawn at `(-2.0, 0.5)` has `initial_pose` `(0, 0)`.
