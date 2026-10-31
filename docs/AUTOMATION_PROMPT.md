# Prompt for automating screenshots, videos and results

Paste this into an AI coding agent that has shell access on your laptop (for example Claude Code). Run it from the repo folder, in an **X11** session.

```text
You are an automation engineer with shell access on my Ubuntu 22.04 laptop (NVIDIA RTX 5060,
ROS 2 Humble, X11 session). The current directory is ~/NAV2-Demonstration, a ROS 2 workspace.
Goal: produce ALL README media (screenshots, video, GIF, rosbag, results) with no manual clicking.

RULES
- Read README.md and docs/ first. Run scripts/check_system.sh and fix every [FAIL].
- Show me any command that needs sudo and wait for my approval before running it.
- Run `colcon test` once at the start and report failures. Do not edit anything under src/ unless a run fails and you can show the root cause.
  If you do, explain it and commit it separately.
- Never commit bags, keystores, .mp4 files, or anything under ~/.nav2_demo.
- Do not invent results. Every number in the README must come from a log or file you produced.

TECHNOLOGY TO USE
ros2 launch / ros2 bag; ffmpeg (h264_nvenc if it works, else libx264); xdotool and wmctrl
(window layout); ImageMagick `import` and `identify` (screenshots and checks); xdpyinfo; git.
Install missing capture tools with: scripts/install.sh --capture (after asking me).

STEPS
1. Build: scripts/build.sh, then `source scripts/env.sh`.
2. Worlds to process: tb3_world, house, stage4, aws_house, aws_warehouse.
   - If a world's map is missing (house, stage4, aws_*), build it with
     `scripts/auto_map.sh <world>` (for aws_* run scripts/install_aws_worlds.sh first, ask me).
     Check the saved .pgm is not mostly empty (identify) and show me a preview. If auto-mapping
     fails twice, list the world as "needs manual mapping".
3. For each world run `scripts/capture_demo.sh <world>`. Also run the tb3_world variants
   TURTLEBOT3_MODEL=burger, NAV_PROFILE=rpp, and DYNAMIC=true (one run each, move the
   output folder to media/<world>_<variant> after each run).
   It writes media/<world>/01..05_*.png, demo.mp4, demo.gif, mission.log, result.txt and a
   rosbag in ~/nav2_demo_bags.
4. Verify per world, with commands, not by eye:
   - 5 PNGs exist and are not blank (identify -format "%[standard-deviation]" > 1000).
   - demo.mp4 duration > 20 s (ffprobe) and demo.gif < 15 MB.
   - `ros2 bag info` on the newest bag lists /scan, /odom, /tf and >0 messages.
   - result.txt shows mission_exit_code=0. If not, read launch.log and mission.log,
     diagnose, fix the cause (usually placeholder waypoints/spawn in worlds.yaml:
     verify coordinates with RViz Publish Point), then retry. Maximum 2 retries per world.
5. Update README.md: fill the Demo section with the PNG/GIF paths and the Results table with
   measured outcomes (mission success, duration, whether the obstacle caused a replan, taken
   from the logs). Leave "not run" for anything skipped.
6. Commit on a new branch `media-update` (PNGs, GIFs, README only). Do NOT push.
7. Finish with a table: world | mapped? | mission result | duration | files | problems.
   List the .mp4 paths so I can upload them to YouTube.

STOP AND ASK ME if: a sudo command is needed, a world needs manual mapping, or you are about
to change files under src/.
```

## Things the automation cannot do for you

- Guarantee automatic mapping succeeds; if it fails, map by hand once (`scripts/save_map.sh`).
- Upload videos to YouTube.
- Guarantee that placeholder waypoints are reachable. Verify them once per world.
