"""Single entry point for the whole project.

    ros2 launch nav2-demo nav2-demo.launch.py                       # tb3_world + Nav2
    ros2 launch nav2-demo nav2-demo.launch.py world:=house          # switch world
    ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=slam   # build a map by hand
    ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=explore # build it automatically
    ros2 launch nav2-demo nav2-demo.launch.py nav_profile:=rpp dynamic_obstacles:=true
    ros2 launch nav2-demo nav2-demo.launch.py world:=tb3_world record:=true gpu:=true
    ros2 launch nav2-demo nav2-demo.launch.py model:=burger         # other robot
    ros2 launch nav2-demo nav2-demo.launch.py --show-args           # all options
"""
import os
import tempfile
from datetime import datetime

import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, ExecuteProcess,
                            IncludeLaunchDescription, LogInfo, OpaqueFunction,
                            RegisterEventHandler, SetEnvironmentVariable,
                            TimerAction)
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from nav2_demo import nav_params
from nav2_demo.worlds import load_config, resolve

PKG = 'nav2-demo'

BAG_TOPICS = [
    '/clock', '/tf', '/tf_static', '/scan', '/odom', '/cmd_vel', '/map',
    '/amcl_pose', '/initialpose', '/goal_pose', '/plan', '/local_plan',
    '/local_costmap/costmap', '/joint_states', '/mission_status',
]


def _truthy(value):
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def _include(path, args=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(path),
        launch_arguments=(args or {}).items())


def _base_params(model):
    share = get_package_share_directory('turtlebot3_navigation2')
    distro = os.environ.get('ROS_DISTRO', 'humble')
    for sub in (os.path.join('param', distro), os.path.join('param', 'humble'), 'param'):
        path = os.path.join(share, sub, f'{model}.yaml')
        if os.path.isfile(path):
            return path
    raise RuntimeError(f'Could not find the stock Nav2 params for {model} in {share}/param')


def _enclave_map():
    path = os.path.expanduser('~/.nav2_demo/enclaves.yaml')
    if not os.path.isfile(path):
        raise RuntimeError(
            'security_mode:=pernode needs ~/.nav2_demo/enclaves.yaml. '
            'Run scripts/setup_security_pernode.sh (see docs/SECURITY_HARDENING.md).')
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _setup(context, *_args, **_kwargs):
    def arg(name):
        return LaunchConfiguration(name).perform(context)

    worlds = load_config()['worlds']
    name = arg('world')
    if name not in worlds:
        raise RuntimeError(
            f"Unknown world '{name}'. Available worlds: {', '.join(sorted(worlds))}")
    w = worlds[name]
    mode = arg('mode')
    if mode not in ('nav', 'slam', 'explore'):
        raise RuntimeError("mode must be 'nav', 'slam' or 'explore'")
    model = arg('model')
    if model not in ('burger', 'waffle', 'waffle_pi'):
        raise RuntimeError(
            f"Unknown model '{model}'. Choose one of: burger, waffle, waffle_pi")

    # ---- resolve files, fail early with helpful messages --------------
    world_file = arg('world_file') or resolve(w['world_file'])
    if not os.path.isfile(world_file):
        hint = ''
        if name.startswith('aws_'):
            hint = ' Run scripts/install_aws_worlds.sh first.'
        raise RuntimeError(f'World file not found: {world_file}.{hint}')

    map_file = arg('map') or resolve(w['map'])
    map_name = os.path.splitext(os.path.basename(resolve(w['map'])))[0]
    if mode == 'nav' and not arg('map') and not os.path.isfile(map_file):
        auto = os.path.expanduser(f'~/.nav2_demo/maps/{map_name}.yaml')
        if not os.path.isfile(auto):
            fallback = os.path.expanduser(f'~/.tb3_nav2/maps/{map_name}.yaml')
            if os.path.isfile(fallback):
                auto = fallback
        if os.path.isfile(auto):          # produced by mode:=explore
            map_file = auto
    if mode == 'nav' and not os.path.isfile(map_file):
        raise RuntimeError(
            f'Map not found: {map_file}\n'
            f'Build it first:\n'
            f'  automatic:  scripts/auto_map.sh {name}\n'
            f'  manual:     ros2 launch nav2-demo nav2-demo.launch.py world:={name} mode:=slam\n'
            f'              (drive around, then)  scripts/save_map.sh {map_name}')

    spawn = w.get('spawn', {})
    x_pose = arg('x_pose') or str(spawn.get('x', 0.0))
    y_pose = arg('y_pose') or str(spawn.get('y', 0.0))

    # ---- environment (set both in-process and for children) -----------
    actions = []

    def setenv(key, value):
        os.environ[key] = value
        actions.append(SetEnvironmentVariable(key, value))

    setenv('TURTLEBOT3_MODEL', model)

    tb3_gz = get_package_share_directory('turtlebot3_gazebo')
    model_paths = [os.path.join(tb3_gz, 'models')] + [
        resolve(p) for p in w.get('model_paths', [])]
    existing = os.environ.get('GAZEBO_MODEL_PATH', '')
    setenv('GAZEBO_MODEL_PATH',
           os.pathsep.join(model_paths + ([existing] if existing else [])))

    if _truthy(arg('gpu')):
        # Hybrid (Intel + NVIDIA) laptops: render Gazebo/RViz on the NVIDIA GPU.
        setenv('__NV_PRIME_RENDER_OFFLOAD', '1')
        setenv('__GLX_VENDOR_LIBRARY_NAME', 'nvidia')
        setenv('__VK_LAYER_NV_optimus', 'NVIDIA_only')

    if _truthy(arg('security')):
        keystore = os.path.expanduser(arg('keystore'))
        if not os.path.isdir(keystore):
            raise RuntimeError(
                f'SROS2 keystore not found at {keystore}. Run scripts/setup_security.sh')
        setenv('ROS_SECURITY_KEYSTORE', keystore)
        setenv('ROS_SECURITY_ENABLE', 'true')
        setenv('ROS_SECURITY_STRATEGY', 'Enforce')
        setenv('ROS_SECURITY_ENCLAVE_OVERRIDE', arg('enclave'))

    # Per-node enclaves: our own nodes get a private identity (least privilege)
    node_env = {}
    if _truthy(arg('security')) and arg('security_mode') == 'pernode':
        emap = _enclave_map()
        for node_name in ('mission_server', 'dynamic_obstacles', 'explorer'):
            if node_name in emap:
                node_env[node_name] = {'ROS_SECURITY_ENCLAVE_OVERRIDE': emap[node_name]}

    # ---- Gazebo + robot ------------------------------------------------
    gz_ros = get_package_share_directory('gazebo_ros')
    nodes = [
        _include(os.path.join(gz_ros, 'launch', 'gzserver.launch.py'),
                 {'world': world_file}),
    ]
    if not _truthy(arg('headless')):
        nodes.append(_include(os.path.join(gz_ros, 'launch', 'gzclient.launch.py')))
    nodes += [
        _include(os.path.join(tb3_gz, 'launch', 'robot_state_publisher.launch.py'),
                 {'use_sim_time': 'true'}),
        _include(os.path.join(tb3_gz, 'launch', 'spawn_turtlebot3.launch.py'),
                 {'x_pose': x_pose, 'y_pose': y_pose}),
    ]

    # ---- Nav2 tuning profile -------------------------------------------
    params_file = arg('params_file')
    profile = arg('nav_profile')
    if not params_file and mode in ('nav', 'explore'):
        prof_cfg = nav_params.load_profiles(os.path.join(
            get_package_share_directory(PKG), 'config', 'nav_profiles.yaml'))
        overrides = w.get('nav_overrides', {})
        settings = nav_params.resolve_settings(prof_cfg, profile, model, overrides)
        for pkg in nav_params.required_packages(settings):
            try:
                get_package_share_directory(pkg)
            except Exception:
                raise RuntimeError(
                    f"nav_profile '{profile}' needs package {pkg}: "
                    f"sudo apt install ros-humble-{pkg.replace('_', '-')}")
        out = os.path.join(tempfile.gettempdir(), f'nav2_demo_{name}_{model}_{profile}.yaml')
        params_file = nav_params.build_params_file(
            _base_params(model), prof_cfg, profile, model, overrides, out) or ''
        actions.append(LogInfo(msg=f"nav_profile={profile} params={params_file or 'stock'}"))

    # ---- Nav2 / SLAM / exploration --------------------------------------
    delay = float(arg('nav2_delay'))
    explorer = None
    if mode == 'nav':
        nav_args = {'use_sim_time': 'True', 'map': map_file,
                    'params_file': params_file or _base_params(model)}
        stack = [_include(os.path.join(
            get_package_share_directory('turtlebot3_navigation2'),
            'launch', 'navigation2.launch.py'), nav_args)]
    else:
        stack = [_include(os.path.join(
            get_package_share_directory('turtlebot3_cartographer'),
            'launch', 'cartographer.launch.py'), {'use_sim_time': 'True'})]
        if mode == 'explore':
            nav_args = {'use_sim_time': 'True', 'autostart': 'true',
                        'params_file': params_file or _base_params(model)}
            stack.append(_include(os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch', 'navigation_launch.py'), nav_args))
            explorer = Node(
                package=PKG, executable='explorer', name='explorer', output='screen',
                additional_env=node_env.get('explorer'),
                parameters=[{'use_sim_time': True,
                             'save_path': os.path.expanduser(f'~/.nav2_demo/maps/{map_name}')}])
            stack.append(explorer)
    nodes.append(TimerAction(period=delay, actions=stack))
    if explorer is not None and _truthy(arg('shutdown_on_done')):
        nodes.append(RegisterEventHandler(OnProcessExit(
            target_action=explorer,
            on_exit=[EmitEvent(event=Shutdown(reason='exploration finished'))])))

    # ---- moving obstacles ----------------------------------------------
    if _truthy(arg('dynamic_obstacles')):
        nodes.append(Node(
            package=PKG, executable='dynamic_obstacles', name='dynamic_obstacles',
            output='screen', additional_env=node_env.get('dynamic_obstacles'),
            parameters=[{'use_sim_time': True, 'world': name}]))

    # ---- mission server (our interfaces) --------------------------------
    if mode == 'nav' and _truthy(arg('mission_server')):
        nodes.append(Node(
            package=PKG, executable='mission_server', name='mission_server',
            output='screen', additional_env=node_env.get('mission_server'),
            parameters=[{'use_sim_time': True, 'world': name}]))

    # ---- rosbag ---------------------------------------------------------
    if _truthy(arg('record')):
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = os.path.join(os.path.expanduser(arg('bag_dir')), f'{name}_{stamp}')
        qos_file = os.path.join(get_package_share_directory(PKG),
                                'config', 'qos', 'bag_qos_overrides.yaml')
        cmd = ['ros2', 'bag', 'record', '-o', out_dir,
               '-s', arg('bag_storage'),
               '--qos-profile-overrides-path', qos_file,
               '--compression-mode', 'file', '--compression-format', 'zstd'
               ] + BAG_TOPICS
        nodes.append(ExecuteProcess(cmd=cmd, output='screen', sigterm_timeout='15'))
        actions.append(LogInfo(msg=f'Recording bag to {out_dir}'))

    actions.append(LogInfo(msg=(
        f"world={name} mode={mode} model={model} spawn=({x_pose},{y_pose}) "
        f"map={map_file if mode == 'nav' else '(building a new map)'}")))
    return actions + nodes


def generate_launch_description():
    def declare(name, default, desc):
        return DeclareLaunchArgument(name, default_value=default, description=desc)

    return LaunchDescription([
        declare('world', 'tb3_world',
                'World name from config/worlds.yaml (tb3_world, house, stage4, aws_house, aws_warehouse)'),
        declare('mode', 'nav',
                "'nav' = navigate on a saved map, 'slam' = build a map by hand, "
                "'explore' = build a map automatically"),
        declare('nav_profile', 'default', 'Nav2 tuning: default, tuned, rpp, mppi'),
        declare('dynamic_obstacles', 'false', 'true = spawn moving obstacles'),
        declare('shutdown_on_done', 'true', 'explore mode: stop everything when mapping ends'),
        declare('model', os.environ.get('TURTLEBOT3_MODEL', 'waffle'),
                'TurtleBot3 model: burger, waffle or waffle_pi (default: $TURTLEBOT3_MODEL or waffle)'),
        declare('world_file', '', 'Override: path to any Gazebo .world file'),
        declare('map', '', 'Override: path to a map .yaml file'),
        declare('x_pose', '', 'Override spawn x (Gazebo world frame)'),
        declare('y_pose', '', 'Override spawn y (Gazebo world frame)'),
        declare('headless', 'false', 'true = no Gazebo window (gzserver only)'),
        declare('gpu', 'false', 'true = render on the NVIDIA GPU (PRIME offload)'),
        declare('nav2_delay', '10.0', 'Seconds to wait for Gazebo before starting Nav2'),
        declare('params_file', '', 'Override: Nav2 parameter file'),
        declare('mission_server', 'true', 'Start the RunMission action server'),
        declare('record', 'false', 'true = record a rosbag'),
        declare('bag_dir', '~/nav2_demo_bags', 'Where bags are written'),
        declare('bag_storage', 'sqlite3', "Bag storage plugin: 'sqlite3' or 'mcap'"),
        declare('security', 'false', 'true = enable SROS2 (run scripts/setup_security.sh first)'),
        declare('keystore', '~/.nav2_demo/keystore', 'SROS2 keystore directory'),
        declare('enclave', '/nav2_demo', 'SROS2 enclave name'),
        declare('security_mode', 'shared',
                "'shared' = one enclave for all, 'pernode' = own enclave per project node"),
        OpaqueFunction(function=_setup),
    ])
