"""Build tuned Nav2 parameter files by patching the stock TurtleBot3 file.

Why patch instead of shipping a copy? The stock file always matches the installed
Nav2 version; we only change what we mean to change.

Precedence (later wins):  profile  <  model  <  world nav_overrides
The 'default' profile means "stock TurtleBot3 params, untouched".
"""
import copy
import os

import yaml

ALLOWED_KEYS = {'controller', 'planner', 'inflation_radius',
                'cost_scaling_factor', 'robot_radius'}
COSTMAPS = ('local_costmap', 'global_costmap')
# 'dwb' and 'navfn' are the stock TurtleBot3 choices (left untouched).
STOCK = {'controller': 'dwb', 'planner': 'navfn'}
REQUIRED_PACKAGES = {
    'rpp': 'nav2_regulated_pure_pursuit_controller',
    'mppi': 'nav2_mppi_controller',
    'smac2d': 'nav2_smac_planner',
}


def load_profiles(path):
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_settings(cfg, profile, model, world_overrides=None):
    """Merge profile, model and world settings. Returns {} for the stock profile."""
    profiles = cfg['profiles']
    if profile not in profiles:
        raise ValueError(f"Unknown nav_profile '{profile}'. Available: {', '.join(profiles)}")
    if profile == 'default':
        return {}
    settings = {}
    settings.update(profiles[profile] or {})
    settings.update((cfg.get('models') or {}).get(model, {}) or {})
    settings.update(world_overrides or {})
    bad = set(settings) - ALLOWED_KEYS
    if bad:
        raise ValueError(f'Unknown nav setting(s): {sorted(bad)}. Allowed: {sorted(ALLOWED_KEYS)}')
    for kind, table in (('controller', 'controllers'), ('planner', 'planners')):
        name = settings.get(kind)
        if name and name != STOCK[kind] and name not in cfg[table]:
            raise ValueError(f"Unknown {kind} '{name}'. Available: "
                             f"{STOCK[kind]}, {', '.join(cfg[table])}")
    return settings


def required_packages(settings):
    return [REQUIRED_PACKAGES[settings[k]] for k in ('controller', 'planner')
            if settings.get(k) in REQUIRED_PACKAGES]


def _ros_params(params, node):
    return params.setdefault(node, {}).setdefault('ros__parameters', {})


def apply_settings(params, cfg, settings):
    """Return a patched deep copy of a loaded Nav2 params dict."""
    params = copy.deepcopy(params)
    ctrl = settings.get('controller')
    if ctrl and ctrl != STOCK['controller']:
        _ros_params(params, 'controller_server')['FollowPath'] = \
            copy.deepcopy(cfg['controllers'][ctrl])
    plan = settings.get('planner')
    if plan and plan != STOCK['planner']:
        _ros_params(params, 'planner_server')['GridBased'] = \
            copy.deepcopy(cfg['planners'][plan])
    for cm in COSTMAPS:
        rp = params.setdefault(cm, {}).setdefault(cm, {}).setdefault('ros__parameters', {})
        if 'robot_radius' in settings:
            rp['robot_radius'] = float(settings['robot_radius'])
        for key in ('inflation_radius', 'cost_scaling_factor'):
            if key in settings:
                rp.setdefault('inflation_layer', {})[key] = float(settings[key])
    return params


def build_params_file(base_path, cfg, profile, model, world_overrides, out_path):
    """Write a patched params file and return its path, or None for the stock profile."""
    settings = resolve_settings(cfg, profile, model, world_overrides)
    if not settings:
        return None
    with open(base_path) as f:
        base = yaml.safe_load(f)
    patched = apply_settings(base, cfg, settings)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        yaml.safe_dump(patched, f, sort_keys=False)
    return out_path
