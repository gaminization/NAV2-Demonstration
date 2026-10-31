# Troubleshooting

Start with `./scripts/check_system.sh`.

| Problem | Fix |
|---|---|
| `Package 'nav2-demo' not found` | Run `./scripts/build.sh`, then `source scripts/env.sh` in this terminal |
| `Map not found` for `house`/`stage4` | Build it: `world:=house mode:=slam`, drive around, `./scripts/save_map.sh house_map` |
| `World file not found` for `aws_*` | `./scripts/install_aws_worlds.sh` |
| Gazebo opens, no robot | Wait up to 1 minute on first run, or relaunch |
| Gazebo black screen or crash | `export LIBGL_ALWAYS_SOFTWARE=1`, or `headless:=true`; see [GPU.md](GPU.md) |
| RViz shows no map | Wait for Nav2 (about 15 s). Set Map display durability to Transient Local |
| Robot does not move after a goal | Set the initial pose (RViz **2D Pose Estimate**, or `mission_client` does it) |
| `Timed out waiting for transform` | Everything must run with sim time. Use the launch file; do not start Nav2 by hand |
| One terminal sees no topics | Run `source scripts/env.sh` there (same domain and security settings) |
| `mission_client` says "Mission rejected" | A mission is already running; wait or cancel it |
| Robot refuses doorways | Lower `inflation_radius` (try 0.35) in a copy of the Nav2 params and pass `params_file:=` |
| Robot stuck | `ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap` |
| Robot spawns inside an object | Change `spawn` in `worlds.yaml` or pass `x_pose:= y_pose:=` |
| Leftover Gazebo process | `pkill -f gzserver; pkill -f gzclient` |
| Screen capture fails | Log in with "Ubuntu on Xorg" (gear icon on login screen). Wayland blocks `x11grab` |
