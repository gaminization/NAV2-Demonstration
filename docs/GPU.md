# Using your NVIDIA GPU (RTX 5060 laptop)

## Honest summary

- **CUDA is not used** by Gazebo Classic or Nav2 here. Nothing in this project runs faster because of CUDA.
- The GPU **does help** with: Gazebo and RViz **rendering** (smoother 3D window) and **video encoding** (NVENC) in `scripts/capture_demo.sh`.
- The simulated LiDAR runs on the CPU.

## Setup

1. RTX 50-series GPUs need a **recent NVIDIA driver (570 or newer)**, and on Ubuntu 22.04 usually the newer HWE kernel. Check NVIDIA's and Ubuntu's docs for your exact laptop.
   ```bash
   sudo apt install linux-generic-hwe-22.04     # then reboot
   ubuntu-drivers devices                       # shows recommended driver
   ```
2. Verify: `nvidia-smi` shows the GPU and driver.
3. Launch with the GPU flag:
   ```bash
   ros2 launch nav2-demo nav2-demo.launch.py gpu:=true
   ```
   This sets the PRIME render offload variables for hybrid (Intel + NVIDIA) laptops. If your laptop is set to NVIDIA-only mode (`sudo prime-select nvidia`) it is unnecessary but harmless.

## Check it works

```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia glxinfo | grep "OpenGL renderer"
```
should mention NVIDIA. While Gazebo runs, `nvidia-smi` should list `gzclient` (and `rviz2`).

## If the 3D window is black or crashes

```bash
export LIBGL_ALWAYS_SOFTWARE=1      # slow fallback
```
or use `headless:=true` (no Gazebo window; RViz still opens).
