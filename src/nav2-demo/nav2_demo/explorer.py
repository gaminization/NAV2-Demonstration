"""Autonomous exploration: drive to frontiers until the map is complete, then save it.

Runs alongside Cartographer (builds the map) and Nav2 (drives). Started by
    ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=explore
The launch file shuts everything down when this node exits.
"""
import math
import os
import subprocess
import sys

import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener

from . import frontiers as fr
from .qos import LATCHED


class Explorer(Node):
    def __init__(self):
        super().__init__('explorer')
        self.declare_parameter('save_path', os.path.expanduser('~/.nav2_demo/maps/explored_map'))
        self.declare_parameter('start_delay', 20.0)       # s, let Nav2 become active
        self.declare_parameter('period', 2.0)             # s between decisions
        self.declare_parameter('min_frontier_size', 8)    # cells
        self.declare_parameter('goal_timeout', 90.0)      # s per goal
        self.declare_parameter('done_after', 4)           # empty checks before finishing
        self.declare_parameter('max_runtime', 1200.0)     # s, then save what we have
        self.declare_parameter('robot_frame', 'base_footprint')

        self._save_path = os.path.expanduser(self.get_parameter('save_path').value)
        self._tf = Buffer()
        TransformListener(self._tf, self)
        self._nav = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.create_subscription(OccupancyGrid, 'map', self._on_map, LATCHED)
        self.create_timer(float(self.get_parameter('period').value), self._tick)

        self._map = None
        self._active = None          # goal handle in flight
        self._goal_started = None
        self._goal_cell = None
        self._blacklist = []
        self._empty = 0
        self._t0 = self.get_clock().now()
        self.done = False
        self.success = False
        self.get_logger().info(f'Explorer ready. Map will be saved to {self._save_path}')

    # ---- helpers -----------------------------------------------------
    def _elapsed(self):
        return (self.get_clock().now() - self._t0).nanoseconds / 1e9

    def _on_map(self, msg):
        self._map = msg

    def _robot_xy(self):
        try:
            t = self._tf.lookup_transform('map', self.get_parameter('robot_frame').value,
                                          Time(), timeout=Duration(seconds=0.5))
        except TransformException:
            return None
        return t.transform.translation.x, t.transform.translation.y

    # ---- main loop ---------------------------------------------------
    def _tick(self):
        if self.done:
            return
        if self._elapsed() < self.get_parameter('start_delay').value:
            return
        if self._elapsed() > self.get_parameter('max_runtime').value:
            self.get_logger().warn('max_runtime reached; saving the map as it is')
            return self._finish()
        if self._active is not None:
            if (self.get_clock().now() - self._goal_started).nanoseconds / 1e9 > \
                    self.get_parameter('goal_timeout').value:
                self.get_logger().warn('Goal timed out; canceling and blacklisting it')
                self._blacklist.append(self._goal_cell)
                self._active.cancel_goal_async()
                self._active = None
            return
        if self._map is None or not self._nav.server_is_ready():
            return
        pose = self._robot_xy()
        if pose is None:
            return

        m = self._map
        grid = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)
        origin = (m.info.origin.position.x, m.info.origin.position.y)
        res = m.info.resolution
        mask = fr.find_frontier_cells(grid)
        clusters = fr.cluster_frontiers(mask, self.get_parameter('min_frontier_size').value)
        robot_cell = fr.world_to_cell(pose, origin, res)
        target = fr.choose_frontier(clusters, robot_cell, res, self._blacklist)

        if target is None:
            self._empty += 1
            self.get_logger().info(
                f'No reachable frontier ({self._empty}/{self.get_parameter("done_after").value})')
            if self._empty >= self.get_parameter('done_after').value:
                self._finish()
            return
        self._empty = 0
        x, y = fr.cell_to_world(target, origin, res)
        self._send_goal(x, y, pose, target, len(clusters))

    def _send_goal(self, x, y, robot_xy, cell, n_clusters):
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        yaw = math.atan2(y - robot_xy[1], x - robot_xy[0])
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)
        self.get_logger().info(f'Frontier goal ({x:.2f}, {y:.2f}); {n_clusters} frontier clusters')
        self._goal_cell = cell
        self._goal_started = self.get_clock().now()
        self._active = True  # placeholder until the goal is accepted
        self._nav.send_goal_async(goal).add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self._blacklist.append(self._goal_cell)
            self._active = None
            return
        self._active = handle
        handle.get_result_async().add_done_callback(self._on_result)

    def _on_result(self, future):
        status = future.result().status
        if status != GoalStatus.STATUS_SUCCEEDED:
            self._blacklist.append(self._goal_cell)
        self._active = None

    # ---- finishing ---------------------------------------------------
    def _finish(self):
        self.done = True
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        self.get_logger().info('Exploration finished. Saving map...')
        cmd = ['ros2', 'run', 'nav2_map_server', 'map_saver_cli', '-f', self._save_path,
               '--ros-args', '-p', 'use_sim_time:=true']
        try:
            subprocess.run(cmd, check=True, timeout=90)
        except (subprocess.SubprocessError, OSError) as exc:
            self.get_logger().error(f'Map save failed: {exc}')
            return
        self.success = os.path.isfile(self._save_path + '.yaml')
        if self.success:
            self.get_logger().info(f'Saved {self._save_path}.yaml')


def main():
    rclpy.init()
    node = Explorer()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.2)
    except KeyboardInterrupt:
        pass
    ok = node.success
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
