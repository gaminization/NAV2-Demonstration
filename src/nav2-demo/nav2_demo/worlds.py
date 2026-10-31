"""Helpers to read config/worlds.yaml and resolve resource specs to file paths."""
import os

import yaml
from ament_index_python.packages import get_package_share_directory

PKG = 'nav2-demo'


def config_path():
    return os.path.join(get_package_share_directory(PKG), 'config', 'worlds.yaml')


def load_config():
    with open(config_path()) as f:
        return yaml.safe_load(f)


def resolve(spec):
    """Turn a resource spec into an absolute path.

    Accepted forms:
      "/abs/path"                         plain path (~ is expanded)
      {package: pkg, path: rel/path}      relative to an installed package's share dir
      {home: .nav2_demo/aws, path: rel}   relative to ~/<home>
    """
    if isinstance(spec, str):
        return os.path.expanduser(spec)
    if 'package' in spec:
        base = get_package_share_directory(spec['package'])
    elif 'home' in spec:
        base = os.path.join(os.path.expanduser('~'), spec['home'])
    else:
        base = ''
    return os.path.normpath(os.path.join(base, spec.get('path', '')))
