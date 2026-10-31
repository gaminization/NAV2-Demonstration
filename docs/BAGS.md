# Recording and replaying data (rosbag2)

## Record while simulating

```bash
ros2 launch nav2-demo nav2-demo.launch.py world:=tb3_world record:=true
```
Bags go to `~/nav2_demo_bags/<world>_<timestamp>/` (change with `bag_dir:=`). They are compressed with zstd. Stop with Ctrl+C and wait a few seconds for the bag to close properly.

Recorded topics: `/clock /tf /tf_static /scan /odom /cmd_vel /map /amcl_pose /initialpose /goal_pose /plan /local_plan /local_costmap/costmap /joint_states /mission_status`.

Use `bag_storage:=mcap` for the MCAP format (opens in Foxglove). Requires `ros-humble-rosbag2-storage-mcap` (installed by `install.sh`).

## Inspect and replay

```bash
source scripts/env.sh
ros2 bag info ~/nav2_demo_bags/tb3_world_YYYYMMDD_HHMMSS
ros2 bag play ~/nav2_demo_bags/tb3_world_YYYYMMDD_HHMMSS --clock
```
In a second terminal run `rviz2 --ros-args -p use_sim_time:=true` and add the displays you want. Do not run the simulator at the same time.

## Notes

- Bags can be large. They are in `.gitignore`: never commit them.
- Bags are not encrypted. They may contain your map and robot trajectory.
