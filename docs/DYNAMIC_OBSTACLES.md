# Moving obstacles

```bash
ros2 launch nav2-demo nav2-demo.launch.py world:=tb3_world dynamic_obstacles:=true
```

Orange cylinders patrol back and forth along a line. They are real Gazebo models, so the LiDAR sees them and Nav2 avoids them or replans.

## Configure

In `config/worlds.yaml`, per world:

```yaml
dynamic_obstacles:
  - {name: walker1, start: {x: 0.5, y: 1.0}, end: {x: 0.5, y: -1.0}, speed: 0.15}
```

`start` and `end` are in the **Gazebo world** frame (metres), `speed` in m/s. Add as many entries as you like.

## How it works

`dynamic_obstacles` node: spawns each model via `/spawn_entity`, with the `libgazebo_ros_planar_move` plugin. It publishes `Twist` on `/dyn_<name>/cmd_vel` and reads `/dyn_<name>/odom` (relative to the start point) to turn around at the ends.

## Tips

- Pick paths that cross the robot's route but do not pass through walls. The coordinates in `worlds.yaml` are placeholders.
- Slow speeds (0.1 to 0.2 m/s) make the demo easier to follow.
- Do not map with moving obstacles on.
- If the cylinder falls or drifts, check that the `gazebo_ros_planar_move` plugin loaded (`ros2 topic list | grep dyn_`).
- Logic (SDF and patrol) is unit-tested; the live behaviour has not been run by the author.
