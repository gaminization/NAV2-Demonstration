# Tests and CI

## Run the tests

```bash
./scripts/build.sh
source scripts/env.sh
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

Or directly: `python3 -m pytest src/nav2-demo/test`.

## What is tested

| File | Covers |
|---|---|
| `test_frontiers.py` | Frontier detection, clustering, goal choice, blacklist |
| `test_nav_params.py` | Profile precedence, controller/planner patching, file generation |
| `test_worlds.py` | `worlds.yaml` schema, resource resolution |
| `test_dyn_model.py` | Moving-obstacle SDF and patrol logic |
| `test_policy_tools.py` | SROS2 policy filtering |
| `test_launch_args.py` | Every launch argument used is declared |

These are fast logic tests with no simulator. They do **not** prove that Gazebo or Nav2 behave; run the demo for that.

## GitHub Actions (`.github/workflows/ci.yml`)

| Job | Does |
|---|---|
| `lint` | Python syntax, YAML validity, ShellCheck |
| `build-and-test` | Installs ROS 2 Humble, `colcon build`, `colcon test`, checks interfaces and `--show-args` |
| `docker-build` | Builds `docker/Dockerfile` |

Not yet automated: a headless simulation smoke test (heavy for free CI runners).
