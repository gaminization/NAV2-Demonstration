# Nav2 tuning profiles

```bash
ros2 launch nav2-demo nav2-demo.launch.py nav_profile:=rpp
```

| Profile | Controller | Planner | Notes |
|---|---|---|---|
| `default` | DWB | NavFn | Stock TurtleBot3 parameters, untouched |
| `tuned` | DWB | NavFn | Better inflation for tight spaces |
| `rpp` | Regulated Pure Pursuit | Smac 2D | Smoother path following |
| `mppi` | MPPI | Smac 2D | Sampling-based, smooth around obstacles. Experimental |

## How it works

The launch file loads the stock TurtleBot3 params for your model and **patches** only what the profile asks for, then writes the result to `/tmp/nav2_demo_<world>_<model>_<profile>.yaml` and passes it to Nav2. This always matches your installed Nav2 version.

Precedence, later wins: **profile**, then **model** (`models:` in `config/nav_profiles.yaml`, for example `burger: robot_radius 0.12`), then **world** (`nav_overrides:` in `worlds.yaml`, for example narrower inflation in the house). `default` ignores model and world overrides.

Settings you can change: `controller`, `planner`, `inflation_radius`, `cost_scaling_factor`, `robot_radius`.

## Required packages

`rpp` and Smac come with Nav2. `mppi` needs `ros-humble-nav2-mppi-controller`. If a package is missing the launch stops with the apt command to run.

## Comparing profiles

```bash
for p in default tuned rpp; do
  NAV_PROFILE=$p scripts/capture_demo.sh tb3_world
  mv media/tb3_world media/tb3_world_$p
done
```

## Honest status

The profile numbers are sensible starting points, **not** tuned results. The merge logic is unit-tested (`test_nav_params.py`); behaviour in Gazebo is not. Expect to adjust lookahead, speeds and inflation per world.
