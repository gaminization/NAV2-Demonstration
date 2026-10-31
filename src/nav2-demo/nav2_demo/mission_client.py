"""Send the waypoint mission of a world (from worlds.yaml) to the mission server.

    ros2 run nav2-demo mission_client                 # world auto-detected
    ros2 run nav2-demo mission_client --world house --no-init
"""
import argparse
import math
import sys
import time

import rclpy
import rclpy.utilities
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient

from nav2_demo_interfaces.action import RunMission
from nav2_demo_interfaces.msg import MissionStatus
from nav2_demo_interfaces.srv import SetInitialPose

from .qos import LATCHED
from .worlds import load_config


def make_pose(x, y, yaw_deg):
    p = PoseStamped()
    p.header.frame_id = 'map'          # stamp 0 = "use latest transform"
    p.pose.position.x = float(x)
    p.pose.position.y = float(y)
    yaw = math.radians(yaw_deg)
    p.pose.orientation.z = math.sin(yaw / 2.0)
    p.pose.orientation.w = math.cos(yaw / 2.0)
    return p


def detect_world(node):
    seen = {}
    node.create_subscription(
        MissionStatus, 'mission_status',
        lambda m: seen.setdefault('world', m.world), LATCHED)
    end = time.time() + 5.0
    while 'world' not in seen and time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.2)
    return seen.get('world')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('--world', help='world name (default: ask the mission server)')
    ap.add_argument('--no-init', action='store_true',
                    help='do not publish the initial pose (already set in RViz)')
    ap.add_argument('--settle', type=float, default=5.0,
                    help='seconds to wait after setting the initial pose')
    args = ap.parse_args(rclpy.utilities.remove_ros_args(sys.argv)[1:])

    rclpy.init()
    node = rclpy.create_node('mission_client')
    try:
        world = args.world or detect_world(node)
        worlds = load_config()['worlds']
        if not world or world not in worlds:
            print(f"Unknown world {world!r}. Use --world one of: {', '.join(worlds)}")
            return 2
        w = worlds[world]
        print(f'World: {world}')

        if not args.no_init:
            cli = node.create_client(SetInitialPose, 'set_initial_pose')
            if not cli.wait_for_service(timeout_sec=10.0):
                print('set_initial_pose service not found. Is the mission server running?')
                return 1
            ip = w['initial_pose']
            req = SetInitialPose.Request()
            req.x, req.y = float(ip['x']), float(ip['y'])
            req.yaw = math.radians(ip.get('yaw', 0.0))
            fut = cli.call_async(req)
            rclpy.spin_until_future_complete(node, fut)
            print(f'Initial pose set; waiting {args.settle:.0f}s for AMCL to settle')
            time.sleep(args.settle)

        client = ActionClient(node, RunMission, 'run_mission')
        if not client.wait_for_server(timeout_sec=10.0):
            print('run_mission action not found. Is the mission server running?')
            return 1

        goal = RunMission.Goal()
        goal.mission_name = f'{world}_demo'
        goal.waypoints = [make_pose(p['x'], p['y'], p.get('yaw', 0.0))
                          for p in w['waypoints']]
        names = [p.get('name', f'waypoint {i + 1}') for i, p in enumerate(w['waypoints'])]

        def on_fb(msg):
            i = msg.feedback.current_waypoint
            label = names[i] if i < len(names) else i
            print(f'-> heading to {label} ({i + 1}/{msg.feedback.total_waypoints})')

        send = client.send_goal_async(goal, feedback_callback=on_fb)
        rclpy.spin_until_future_complete(node, send)
        handle = send.result()
        if not handle.accepted:
            print('Mission rejected (is another mission running?)')
            return 1

        res_future = handle.get_result_async()
        try:
            rclpy.spin_until_future_complete(node, res_future)
        except KeyboardInterrupt:
            print('\nCanceling mission...')
            handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, res_future)
        res = res_future.result().result
        print(f'Result: success={res.success} reached={res.waypoints_reached} '
              f'message={res.message!r}')
        return 0 if res.success else 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
