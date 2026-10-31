"""Mission server: a clean interface on top of Nav2's FollowWaypoints.

Provides
  action  run_mission       (nav2_demo_interfaces/action/RunMission)
  service set_initial_pose  (nav2_demo_interfaces/srv/SetInitialPose)
  topic   mission_status    (nav2_demo_interfaces/msg/MissionStatus, latched)
"""
import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.action import FollowWaypoints
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from nav2_demo_interfaces.action import RunMission
from nav2_demo_interfaces.msg import MissionStatus
from nav2_demo_interfaces.srv import SetInitialPose

from .qos import LATCHED


class MissionServer(Node):
    def __init__(self):
        super().__init__('mission_server')
        self.declare_parameter('world', 'unknown')
        self._world = self.get_parameter('world').value
        self._busy = False
        group = ReentrantCallbackGroup()

        self._status_pub = self.create_publisher(MissionStatus, 'mission_status', LATCHED)
        self._pose_pub = self.create_publisher(
            PoseWithCovarianceStamped, 'initialpose', LATCHED)
        self._fw = ActionClient(self, FollowWaypoints, 'follow_waypoints',
                                callback_group=group)
        self.create_service(SetInitialPose, 'set_initial_pose',
                            self._on_set_initial_pose, callback_group=group)
        self._server = ActionServer(
            self, RunMission, 'run_mission',
            execute_callback=self._execute,
            goal_callback=self._on_goal,
            cancel_callback=lambda _: CancelResponse.ACCEPT,
            callback_group=group)

        self._publish_status(MissionStatus.STATE_IDLE, '', 0, 0)
        self.get_logger().info(f"Mission server ready (world='{self._world}')")

    # ---- helpers -------------------------------------------------------
    def _publish_status(self, state, mission, current, total):
        msg = MissionStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.world = self._world
        msg.mission_name = mission
        msg.state = state
        msg.current_waypoint = int(current)
        msg.total_waypoints = int(total)
        self._status_pub.publish(msg)

    # ---- service -------------------------------------------------------
    def _on_set_initial_pose(self, request, response):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.position.x = request.x
        msg.pose.pose.position.y = request.y
        msg.pose.pose.orientation.z = math.sin(request.yaw / 2.0)
        msg.pose.pose.orientation.w = math.cos(request.yaw / 2.0)
        cov = [0.0] * 36
        cov[0] = 0.25
        cov[7] = 0.25
        cov[35] = 0.0685
        msg.pose.covariance = cov
        self._pose_pub.publish(msg)
        response.success = True
        response.message = 'initial pose published'
        return response

    # ---- action --------------------------------------------------------
    def _on_goal(self, goal_request):
        if self._busy:
            self.get_logger().warn('Rejecting mission: another mission is running')
            return GoalResponse.REJECT
        if len(goal_request.waypoints) == 0:
            self.get_logger().warn('Rejecting mission: no waypoints')
            return GoalResponse.REJECT
        self._busy = True
        return GoalResponse.ACCEPT

    def _execute(self, goal_handle):
        req = goal_handle.request
        name = req.mission_name or 'unnamed'
        total = len(req.waypoints)
        result = RunMission.Result()
        last = {'cur': 0}
        S = MissionStatus
        try:
            if not self._fw.wait_for_server(timeout_sec=10.0):
                return self._end(goal_handle, result, 'abort', S.STATE_FAILED, name,
                                 0, total, 'follow_waypoints not available: is Nav2 running?')

            nav_goal = FollowWaypoints.Goal()
            nav_goal.poses = list(req.waypoints)

            def on_feedback(msg):
                cur = int(msg.feedback.current_waypoint)
                last['cur'] = cur
                self._publish_status(S.STATE_RUNNING, name, cur, total)
                fb = RunMission.Feedback()
                fb.current_waypoint = cur
                fb.total_waypoints = total
                goal_handle.publish_feedback(fb)

            self._publish_status(S.STATE_RUNNING, name, 0, total)
            send = self._fw.send_goal_async(nav_goal, feedback_callback=on_feedback)
            while not send.done():
                time.sleep(0.05)
            nav_handle = send.result()
            if not nav_handle.accepted:
                return self._end(goal_handle, result, 'abort', S.STATE_FAILED, name,
                                 0, total, 'Nav2 rejected the waypoint goal')

            res_future = nav_handle.get_result_async()
            cancel_sent = False
            while not res_future.done():
                if goal_handle.is_cancel_requested and not cancel_sent:
                    nav_handle.cancel_goal_async()
                    cancel_sent = True
                time.sleep(0.1)

            nav_res = res_future.result()
            missed = [int(getattr(m, 'index', m))
                      for m in nav_res.result.missed_waypoints]
            result.missed_waypoints = missed
            if nav_res.status == GoalStatus.STATUS_SUCCEEDED and not missed:
                return self._end(goal_handle, result, 'succeed', S.STATE_SUCCEEDED, name,
                                 total, total, 'all waypoints reached')
            if cancel_sent or nav_res.status == GoalStatus.STATUS_CANCELED:
                return self._end(goal_handle, result, 'cancel', S.STATE_CANCELED, name,
                                 last['cur'], total, 'mission canceled')
            return self._end(goal_handle, result, 'abort', S.STATE_FAILED, name,
                             last['cur'], total, f'missed waypoints: {missed}')
        finally:
            self._busy = False

    def _end(self, goal_handle, result, how, state, name, reached, total, message):
        result.success = (how == 'succeed')
        result.message = message
        result.waypoints_reached = int(reached)
        self._publish_status(state, name, reached, total)
        self.get_logger().info(f'Mission {name}: {message}')
        getattr(goal_handle, {'succeed': 'succeed', 'abort': 'abort',
                              'cancel': 'canceled'}[how])()
        return result


def main():
    rclpy.init()
    node = MissionServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
