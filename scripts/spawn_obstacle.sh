#!/usr/bin/env bash
# Drop a box into the running Gazebo world, or remove it again.
#   scripts/spawn_obstacle.sh spawn  <x> <y> [name]
#   scripts/spawn_obstacle.sh remove [name]
# Coordinates are in the Gazebo WORLD frame.
set -eo pipefail
ACTION="${1:-}"
case "$ACTION" in
  spawn)
    X="${2:?x required}"; Y="${3:?y required}"; NAME="${4:-obstacle_box}"
    SDF="/tmp/${NAME}.sdf"
    cat > "$SDF" << SDFEOF
<?xml version="1.0"?>
<sdf version="1.6">
  <model name="${NAME}">
    <static>true</static>
    <link name="link">
      <collision name="c"><geometry><box><size>0.5 0.5 0.5</size></box></geometry></collision>
      <visual name="v">
        <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
        <material><ambient>0.8 0.1 0.1 1</ambient><diffuse>0.8 0.1 0.1 1</diffuse></material>
      </visual>
    </link>
  </model>
</sdf>
SDFEOF
    ros2 run gazebo_ros spawn_entity.py -entity "$NAME" -file "$SDF" -x "$X" -y "$Y" -z 0.25
    ;;
  remove)
    NAME="${2:-obstacle_box}"
    ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: '${NAME}'}"
    ;;
  *)
    echo "Usage: $0 spawn <x> <y> [name] | remove [name]"; exit 1 ;;
esac
