"""Moving-obstacle model + patrol logic (no ROS imports, unit-testable).

The obstacle is a Gazebo model driven by the libgazebo_ros_planar_move plugin:
publish Twist on /<name>/cmd_vel, read its pose on /<name>/odom. The plugin's odometry
starts at (0, 0), so positions from /odom are RELATIVE to the spawn point.
"""
import math
import xml.sax.saxutils as su

SDF_TEMPLATE = """<?xml version="1.0"?>
<sdf version="1.6">
  <model name="{name}">
    <link name="link">
      <gravity>false</gravity>
      <inertial>
        <mass>5.0</mass>
        <inertia><ixx>0.1</ixx><ixy>0</ixy><ixz>0</ixz><iyy>0.1</iyy><iyz>0</iyz><izz>0.1</izz></inertia>
      </inertial>
      <collision name="collision">
        <geometry><cylinder><radius>{radius}</radius><length>{height}</length></cylinder></geometry>
      </collision>
      <visual name="visual">
        <geometry><cylinder><radius>{radius}</radius><length>{height}</length></cylinder></geometry>
        <material><ambient>0.9 0.5 0.1 1</ambient><diffuse>0.9 0.5 0.1 1</diffuse></material>
      </visual>
    </link>
    <plugin name="planar_move" filename="libgazebo_ros_planar_move.so">
      <ros><namespace>/{name}</namespace></ros>
      <update_rate>50</update_rate>
      <publish_rate>20</publish_rate>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>false</publish_odom_tf>
      <odometry_frame>{name}_odom</odometry_frame>
      <robot_base_frame>{name}_base</robot_base_frame>
    </plugin>
  </model>
</sdf>
"""


def make_sdf(name, radius=0.15, height=0.5):
    return SDF_TEMPLATE.format(name=su.escape(name), radius=radius, height=height)


class Patrol:
    """Back-and-forth motion between two points, in coordinates relative to the start."""

    def __init__(self, start_xy, end_xy, speed, tolerance=0.1):
        self.dx = end_xy[0] - start_xy[0]
        self.dy = end_xy[1] - start_xy[1]
        self.speed = float(speed)
        self.tolerance = tolerance
        self.towards_end = True

    def update(self, rel_x, rel_y):
        """Given the current relative position, return the (vx, vy) command."""
        tx, ty = (self.dx, self.dy) if self.towards_end else (0.0, 0.0)
        ex, ey = tx - rel_x, ty - rel_y
        dist = math.hypot(ex, ey)
        if dist < self.tolerance:
            self.towards_end = not self.towards_end
            return 0.0, 0.0
        return self.speed * ex / dist, self.speed * ey / dist
