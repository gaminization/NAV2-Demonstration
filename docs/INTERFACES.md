# ROS interfaces

Package `nav2_demo_interfaces` defines three interfaces. The `mission_server` node (started by the launch file) implements them on top of Nav2.

| Kind | Name | Type | QoS |
|---|---|---|---|
| Action | `/run_mission` | `nav2_demo_interfaces/action/RunMission` | default (reliable) |
| Service | `/set_initial_pose` | `nav2_demo_interfaces/srv/SetInitialPose` | default |
| Topic | `/mission_status` | `nav2_demo_interfaces/msg/MissionStatus` | reliable + transient_local (latched) |

```bash
source scripts/env.sh
ros2 interface show nav2_demo_interfaces/action/RunMission
```

## Examples

```bash
# Where is the robot? Tell AMCL (map frame, yaw in radians)
ros2 service call /set_initial_pose nav2_demo_interfaces/srv/SetInitialPose "{x: -2.0, y: -0.5, yaw: 0.0}"

# What is the mission server doing? (latched: you get the latest value immediately)
ros2 topic echo /mission_status --qos-durability transient_local --qos-reliability reliable

# Send a mission by hand
ros2 action send_goal /run_mission nav2_demo_interfaces/action/RunMission \
"{mission_name: manual, waypoints: [{header: {frame_id: map}, pose: {position: {x: 1.0, y: 1.0}, orientation: {w: 1.0}}}]}" --feedback
```

Or use the ready-made client: `ros2 run nav2-demo mission_client`.

## Behaviour

- One mission at a time; a second goal is rejected.
- Cancel with Ctrl+C in the client (or `ros2 action send_goal` cancel); the robot stops.
- Result `missed_waypoints` lists indexes Nav2 gave up on.

Nav2's own interfaces (`/navigate_to_pose`, `/follow_waypoints`, `/clear_*_costmap`) remain available.
