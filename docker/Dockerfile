# ROS 2 Humble + Gazebo Classic + Nav2 + TurtleBot3 in a container.
# Source code is NOT baked in: docker-compose bind-mounts the repo at /ws.
FROM osrf/ros:humble-desktop

ARG HOST_UID=1000
ARG HOST_GID=1000
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-nav2-simple-commander \
      ros-humble-turtlebot3 ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-navigation2 \
      ros-humble-turtlebot3-cartographer ros-humble-turtlebot3-teleop ros-humble-turtlebot3-msgs \
      ros-humble-gazebo-ros-pkgs ros-humble-cartographer ros-humble-cartographer-ros \
      ros-humble-rosbag2 ros-humble-rosbag2-storage-mcap ros-humble-sros2 \
      python3-colcon-common-extensions python3-yaml git mesa-utils sudo \
      ffmpeg xdotool wmctrl imagemagick x11-utils scrot \
    && rm -rf /var/lib/apt/lists/*

# Optional Nav2 plugins for nav_profile:=rpp / mppi (not fatal if unavailable)
RUN apt-get update && (apt-get install -y --no-install-recommends \
      ros-humble-nav2-regulated-pure-pursuit-controller ros-humble-nav2-smac-planner \
      ros-humble-nav2-mppi-controller || true) && rm -rf /var/lib/apt/lists/*

# Non-root user with the same UID/GID as the host user, so files in the bind mount stay yours.
RUN groupadd -g ${HOST_GID} dev \
 && useradd -m -u ${HOST_UID} -g ${HOST_GID} -s /bin/bash dev \
 && usermod -aG video,render dev \
 && mkdir -p /ws /home/dev/.gazebo /home/dev/nav2_demo_bags /home/dev/.nav2_demo \
 && chown -R dev:dev /ws /home/dev

ENV TURTLEBOT3_MODEL=waffle \
    ROS_DOMAIN_ID=42 \
    ROS_LOCALHOST_ONLY=1 \
    QT_X11_NO_MITSHM=1 \
    HOME=/home/dev

RUN printf '%s\n' \
  'source /opt/ros/humble/setup.bash' \
  '[ -f /ws/install/setup.bash ] && source /ws/install/setup.bash' \
  'cd /ws' >> /home/dev/.bashrc \
 && chown dev:dev /home/dev/.bashrc

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER dev
WORKDIR /ws
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
