# Running in Docker

Use this if you do not want to install ROS on your machine, or you are not on Ubuntu 22.04 (for example Ubuntu 24.04). The image has ROS 2 Humble, Gazebo Classic, Nav2, TurtleBot3, rosbag2 and the capture tools.

**Honest status:** the Docker files were written but not built or run by the author. Expect to fix small things on the first run and please report them.

## What you need on the host

- Linux with an X11 session (or Wayland with XWayland, which most distros enable).
- Docker Engine and the Compose plugin: <https://docs.docker.com/engine/install/ubuntu/>
- `sudo apt install x11-xserver-utils` (for `xhost`)
- Optional, for the NVIDIA GPU: driver 570+ and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

Run Docker without `sudo`: `sudo usermod -aG docker $USER`, then log out and in.

macOS and Windows are not supported for the GUI.

## Quick start

```bash
git clone https://github.com/gaminization/NAV2-Demonstration.git
cd NAV2-Demonstration
./scripts/docker.sh build                      # one time, several minutes
./scripts/docker.sh up tb3_world waffle        # Gazebo + RViz open on your screen
```

The first start also compiles the workspace inside the container (about 1 minute).

In a second terminal:

```bash
./scripts/docker.sh exec ros2 run nav2-demo mission_client
./scripts/docker.sh exec ./scripts/spawn_obstacle.sh spawn -1.2 -0.5
./scripts/docker.sh shell                      # interactive shell in the container
```

Stop: Ctrl+C in the first terminal, then `./scripts/docker.sh down`.

## Options

| Goal | Command |
|---|---|
| Other world | `./scripts/docker.sh up house` |
| Other robot | `./scripts/docker.sh up house burger` |
| NVIDIA GPU | `GPU=1 ./scripts/docker.sh up tb3_world waffle` |
| Build a map | `./scripts/docker.sh up house` is for navigation. For SLAM: `./scripts/docker.sh shell`, then `ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=slam` |
| Record a bag | in a shell: `ros2 launch nav2-demo nav2-demo.launch.py record:=true`. Bags appear in `./bags` on the host |
| Screenshots / video | in a shell: `./scripts/capture_demo.sh tb3_world` (needs an X11 session) |

## How it works

- The repo is **bind-mounted** at `/ws`, so edits on the host appear instantly in the container and saved maps and media land in your repo. `build/`, `install/` and `log/` are created in the repo folder (and are git-ignored).
- The container user has your UID/GID, so files are not owned by root.
- `network_mode: host` and `ROS_LOCALHOST_ONLY=1`: GUI and DDS work, and traffic stays on your machine.
- `~/.nav2_demo` (SROS2 keystore, AWS worlds) and `./bags` are mounted too, so they survive container restarts.
- `xhost +SI:localuser:<you>` lets only your own user's processes draw on your display. `docker.sh down` removes it.

## Troubleshooting

| Problem | Fix |
|---|---|
| `cannot open display` / Qt xcb error | Run `echo $DISPLAY`, then `./scripts/docker.sh up` again (it runs `xhost`). On Wayland make sure XWayland is on |
| Black Gazebo window | Try without `GPU=1`; or install the NVIDIA Container Toolkit; or set `LIBGL_ALWAYS_SOFTWARE=1` in `docker-compose.yml` environment |
| `could not select device driver "nvidia"` | NVIDIA Container Toolkit missing: `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker` |
| Permission denied in `build/` or `install/` | A previous run as root created them: `sudo rm -rf build install log` and retry |
| Changes to `src/` not visible | Run `./scripts/docker.sh exec ./scripts/build.sh` |
| Screen capture fails | Needs an X11 session on the host |
