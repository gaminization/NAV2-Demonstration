import os
from unittest import mock

import yaml

HERE = os.path.dirname(__file__)
WORLDS = yaml.safe_load(open(os.path.join(HERE, '..', 'config', 'worlds.yaml')))['worlds']
REQUIRED = ('description', 'world_file', 'map', 'spawn', 'initial_pose', 'waypoints',
            'demo_obstacle')


def test_every_world_has_required_keys():
    for name, w in WORLDS.items():
        for key in REQUIRED:
            assert key in w, f'{name} is missing {key}'


def test_waypoints_and_obstacles_are_well_formed():
    for name, w in WORLDS.items():
        assert len(w['waypoints']) >= 2, name
        for p in w['waypoints']:
            assert 'x' in p and 'y' in p, (name, p)
        for ob in w.get('dynamic_obstacles', []):
            assert {'name', 'start', 'end'} <= set(ob), (name, ob)


def test_resolve_specs():
    with mock.patch('ament_index_python.packages.get_package_share_directory',
                    lambda pkg: f'/fake/{pkg}'):
        from nav2_demo import worlds
        with mock.patch.object(worlds, 'get_package_share_directory', lambda pkg: f'/fake/{pkg}'):
            assert worlds.resolve({'package': 'p', 'path': 'a/b.yaml'}) == '/fake/p/a/b.yaml'
            home = os.path.expanduser('~')
            assert worlds.resolve({'home': '.x', 'path': 'm.yaml'}) == f'{home}/.x/m.yaml'
            assert worlds.resolve('/abs/path') == '/abs/path'


def test_nav_profile_names_in_worlds_are_valid_settings():
    from nav2_demo import nav_params
    for name, w in WORLDS.items():
        assert set(w.get('nav_overrides', {})) <= nav_params.ALLOWED_KEYS, name
