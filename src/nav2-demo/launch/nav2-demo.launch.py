"""Launch TurtleBot3 in Gazebo together with the Nav2 stack and RViz.

Examples:
  ros2 launch nav2-demo nav2-demo.launch.py
  ros2 launch nav2-demo nav2-demo.launch.py world:=house map:=$HOME/maps/house.yaml
  ros2 launch nav2-demo nav2-demo.launch.py set_initial_pose:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, OpaqueFunction,
                            SetEnvironmentVariable, TimerAction)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

WORLD_LAUNCH_FILES = {
    'world': 'turtlebot3_world.launch.py',
    'house': 'turtlebot3_house.launch.py',
}


def launch_setup(context):
    world = LaunchConfiguration('world').perform(context)
    map_file = LaunchConfiguration('map').perform(context)
    params_file = LaunchConfiguration('params_file').perform(context)
    model = LaunchConfiguration('model').perform(context)
    nav_delay = float(LaunchConfiguration('nav_delay').perform(context))
    set_pose = LaunchConfiguration('set_initial_pose').perform(context).lower() == 'true'
    x = LaunchConfiguration('x_pose').perform(context)
    y = LaunchConfiguration('y_pose').perform(context)

    # Ensure os.environ has TURTLEBOT3_MODEL set for python launch scripts
    os.environ['TURTLEBOT3_MODEL'] = model

    if world not in WORLD_LAUNCH_FILES:
        raise RuntimeError(f"world must be one of {list(WORLD_LAUNCH_FILES)}, got '{world}'")

    gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    nav_dir = get_package_share_directory('turtlebot3_navigation2')

    # Default map = the prebuilt map that matches the default world.
    if not map_file:
        map_file = os.path.join(nav_dir, 'map', 'map.yaml')

    # Default params = TurtleBot3 model navigation params.
    # We must explicitly resolve and pass this because gazebo_ros sets
    # 'params_file' to an empty string in the launch context, which would
    # otherwise cause nav2's RewrittenYaml to fail opening ''.
    if not params_file:
        ros_distro = os.environ.get('ROS_DISTRO', 'humble')
        param_file_name = f'{model}.yaml'
        candidate_path = os.path.join(nav_dir, 'param', ros_distro, param_file_name)
        if not os.path.exists(candidate_path):
            candidate_path = os.path.join(nav_dir, 'param', param_file_name)
        params_file = candidate_path

    actions = [SetEnvironmentVariable('TURTLEBOT3_MODEL', model)]

    # 1) Gazebo + robot
    actions.append(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_dir, 'launch', WORLD_LAUNCH_FILES[world]))))

    # 2) Nav2 + RViz (delayed so Gazebo and the robot are up first)
    actions.append(TimerAction(period=nav_delay, actions=[
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav_dir, 'launch', 'navigation2.launch.py')),
            launch_arguments={
                'use_sim_time': 'True',
                'map': map_file,
                'params_file': params_file,
            }.items())
    ]))

    # 3) Optionally publish the initial pose so you don't have to click in RViz
    if set_pose:
        pose_msg = (
            "{header: {frame_id: map}, pose: {pose: {position: "
            f"{{x: {x}, y: {y}, z: 0.0}}, orientation: {{w: 1.0}}}}, "
            "covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "
            "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}")
        actions.append(TimerAction(period=nav_delay + 12.0, actions=[
            ExecuteProcess(
                cmd=['ros2', 'topic', 'pub', '--once', '--qos-reliability', 'reliable',
                     '/initialpose', 'geometry_msgs/msg/PoseWithCovarianceStamped',
                     pose_msg],
                output='screen')
        ]))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='world',
                              description="'world' (default arena) or 'house'"),
        DeclareLaunchArgument('map', default_value='',
                              description='Path to map .yaml (default: prebuilt TB3 world map)'),
        DeclareLaunchArgument('params_file', default_value='',
                              description='Path to Nav2 params .yaml (default: TB3 model config)'),
        DeclareLaunchArgument('model', default_value='waffle',
                              description='TurtleBot3 model: waffle or burger'),
        DeclareLaunchArgument('nav_delay', default_value='8.0',
                              description='Seconds to wait for Gazebo before starting Nav2'),
        DeclareLaunchArgument('set_initial_pose', default_value='true',
                              description='Auto-publish the initial pose to AMCL'),
        DeclareLaunchArgument('x_pose', default_value='-2.0',
                              description='Initial pose x (matches robot spawn)'),
        DeclareLaunchArgument('y_pose', default_value='-0.5',
                              description='Initial pose y (matches robot spawn)'),
        OpaqueFunction(function=launch_setup),
    ])
