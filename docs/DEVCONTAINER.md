# VS Code dev container

Open the project inside the Docker image with VS Code's Python support, ROS extension and pytest already wired up.

1. Install Docker and VS Code with the **Dev Containers** extension.
2. Open the repo folder in VS Code, then **Reopen in Container** (command palette).
3. First start builds the image and compiles the workspace (several minutes).
4. In the container terminal:
   ```bash
   source scripts/env.sh
   ros2 launch nav2-demo nav2-demo.launch.py
   ```
   Gazebo and RViz appear on your desktop (X11 forwarding, same as [DOCKER.md](DOCKER.md)).

Run the tests from the Testing sidebar, or: `colcon test --event-handlers console_direct+`.

## GPU

Add `"--gpus", "all"` to `runArgs` in `.devcontainer/devcontainer.json` (needs the NVIDIA Container Toolkit), then launch with `gpu:=true`.

## Notes

- Same image as `docker-compose.yml`, so behaviour matches.
- Your repo is bind-mounted at `/ws`; `~/.nav2_demo` is mounted so maps and keys persist.
- Not tested by the author. If the window does not open, run `xhost +SI:localuser:$(id -un)` on the host.
