# Choosing the TurtleBot3 model

```bash
ros2 launch nav2-demo nav2-demo.launch.py model:=burger
```

`model:=` accepts `burger`, `waffle` (default) or `waffle_pi`. If you leave it out, the launch file uses `$TURTLEBOT3_MODEL` (set to `waffle` by `scripts/env.sh`), so these also work:

```bash
TURTLEBOT3_MODEL=burger ros2 launch nav2-demo nav2-demo.launch.py
TURTLEBOT3_MODEL=burger scripts/capture_demo.sh tb3_world
TURTLEBOT3_MODEL=burger scripts/docker.sh up house       # Docker
scripts/docker.sh up house burger                        # Docker, explicit
```

| Model | Size (approx.) | Sensors | Notes |
|---|---|---|---|
| `burger` | 138 x 178 mm | 2D LiDAR | Smallest. Good for tight doorways and narrow aisles |
| `waffle` | 281 x 306 mm | 2D LiDAR + depth camera | Default. Largest footprint |
| `waffle_pi` | 281 x 306 mm | 2D LiDAR + camera | Same body as waffle, Raspberry Pi camera |

What changes automatically:

- The robot that Gazebo spawns.
- The Nav2 parameter file (the TurtleBot3 launch picks `burger.yaml`, `waffle.yaml` or `waffle_pi.yaml`). Footprint and speed limits come from there.
- Nothing else. Nav2 here uses the LiDAR only, so the cameras do not affect navigation.

Tips:

- Maps built with one model work with the others, but a bigger robot needs wider gaps. If a bigger robot refuses a doorway, see "Robot refuses doorways" in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
- Bags and screenshots do not include the model name; change `bag_dir:=` or the output folder if you compare models.
