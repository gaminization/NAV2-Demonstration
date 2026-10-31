"""Send ONE goal with Nav2's Simple Commander (simplest possible example).

    ros2 run nav2-demo nav_goal --x 1.0 --y 0.5 --yaw 90 --world tb3_world
"""
import argparse
import math
import sys

import rclpy
import rclpy.utilities
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from .worlds import load_config


def make_pose(x, y, yaw_deg):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.pose.position.x = float(x)
    p.pose.position.y = float(y)
    yaw = math.radians(yaw_deg)
    p.pose.orientation.z = math.sin(yaw / 2.0)
    p.pose.orientation.w = math.cos(yaw / 2.0)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('--x', type=float, required=True)
    ap.add_argument('--y', type=float, required=True)
    ap.add_argument('--yaw', type=float, default=0.0, help='degrees')
    ap.add_argument('--world', help='use this world\'s initial pose')
    ap.add_argument('--skip-initial-pose', action='store_true')
    args = ap.parse_args(rclpy.utilities.remove_ros_args(sys.argv)[1:])

    rclpy.init()
    nav = BasicNavigator()
    if not args.skip_initial_pose:
        ip = {'x': 0.0, 'y': 0.0, 'yaw': 0.0}
        if args.world:
            ip = load_config()['worlds'][args.world]['initial_pose']
        nav.setInitialPose(make_pose(ip['x'], ip['y'], ip.get('yaw', 0.0)))
    nav.waitUntilNav2Active()

    nav.goToPose(make_pose(args.x, args.y, args.yaw))
    while not nav.isTaskComplete():
        fb = nav.getFeedback()
        if fb:
            print(f'Distance remaining: {fb.distance_remaining:.2f} m', end='\r')
    print()
    result = nav.getResult()
    print({TaskResult.SUCCEEDED: 'Goal reached!',
           TaskResult.CANCELED: 'Goal canceled.',
           TaskResult.FAILED: 'Goal failed.'}.get(result, 'Unknown result'))
    rclpy.shutdown()


if __name__ == '__main__':
    main()
