"""Spawn moving obstacles in Gazebo and patrol them back and forth.

Configured per world in worlds.yaml under `dynamic_obstacles`. Started by
    ros2 launch nav2-demo nav2-demo.launch.py dynamic_obstacles:=true
"""
import sys

import rclpy
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node

from .dyn_model import Patrol, make_sdf
from .qos import RELIABLE
from .worlds import load_config


class DynamicObstacles(Node):
    def __init__(self):
        super().__init__('dynamic_obstacles')
        self.declare_parameter('world', 'tb3_world')
        world = self.get_parameter('world').value
        self._cfg = load_config()['worlds'][world].get('dynamic_obstacles', [])
        self._pos = {}
        self._patrols = {}
        self._pubs = {}
        if not self._cfg:
            self.get_logger().warn(f"World '{world}' defines no dynamic_obstacles")

    def spawn_all(self):
        client = self.create_client(SpawnEntity, '/spawn_entity')
        while not client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('Waiting for Gazebo /spawn_entity ...')
            if not rclpy.ok():
                return False
        for ob in self._cfg:
            name = f"dyn_{ob['name']}"
            req = SpawnEntity.Request()
            req.name = name
            req.xml = make_sdf(name)
            req.initial_pose.position.x = float(ob['start']['x'])
            req.initial_pose.position.y = float(ob['start']['y'])
            req.initial_pose.position.z = 0.25
            req.initial_pose.orientation.w = 1.0
            req.reference_frame = 'world'
            fut = client.call_async(req)
            rclpy.spin_until_future_complete(self, fut)
            res = fut.result()
            if res is None or not res.success:
                self.get_logger().error(f'Spawn of {name} failed: '
                                        f'{getattr(res, "status_message", "no response")}')
                continue
            self._patrols[name] = Patrol(
                (ob['start']['x'], ob['start']['y']), (ob['end']['x'], ob['end']['y']),
                ob.get('speed', 0.15))
            self._pos[name] = (0.0, 0.0)
            self._pubs[name] = self.create_publisher(Twist, f'/{name}/cmd_vel', RELIABLE)
            self.create_subscription(
                Odometry, f'/{name}/odom',
                lambda msg, n=name: self._pos.__setitem__(
                    n, (msg.pose.pose.position.x, msg.pose.pose.position.y)),
                RELIABLE)
            self.get_logger().info(f'Spawned moving obstacle {name}')
        self.create_timer(0.05, self._control)
        return True

    def _control(self):
        for name, patrol in self._patrols.items():
            vx, vy = patrol.update(*self._pos[name])
            msg = Twist()
            msg.linear.x, msg.linear.y = vx, vy
            self._pubs[name].publish(msg)


def main():
    rclpy.init()
    node = DynamicObstacles()
    try:
        if node._cfg and node.spawn_all():
            rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(0)


if __name__ == '__main__':
    main()
