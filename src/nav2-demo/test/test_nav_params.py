import os

import yaml

from nav2_demo import nav_params as npar

HERE = os.path.dirname(__file__)
CFG = yaml.safe_load(open(os.path.join(HERE, '..', 'config', 'nav_profiles.yaml')))

BASE = {
    'controller_server': {'ros__parameters': {'FollowPath': {'plugin': 'dwb_core::DWBLocalPlanner'}}},
    'planner_server': {'ros__parameters': {'GridBased': {'plugin': 'nav2_navfn_planner/NavfnPlanner'}}},
    'local_costmap': {'local_costmap': {'ros__parameters': {
        'robot_radius': 0.22, 'inflation_layer': {'inflation_radius': 1.0}}}},
    'global_costmap': {'global_costmap': {'ros__parameters': {
        'robot_radius': 0.22, 'inflation_layer': {'inflation_radius': 1.0}}}},
}


def test_default_profile_is_stock():
    assert npar.resolve_settings(CFG, 'default', 'burger', {'inflation_radius': 0.1}) == {}


def test_precedence_world_over_model_over_profile():
    s = npar.resolve_settings(CFG, 'tuned', 'burger', {'inflation_radius': 0.25})
    assert s['inflation_radius'] == 0.25        # world wins
    assert s['robot_radius'] == 0.12            # model adds
    assert s['cost_scaling_factor'] == 4.0      # profile remains


def test_apply_rpp_and_smac():
    s = npar.resolve_settings(CFG, 'rpp', 'waffle')
    out = npar.apply_settings(BASE, CFG, s)
    rp = out['controller_server']['ros__parameters']['FollowPath']
    assert 'RegulatedPurePursuit' in rp['plugin']
    assert 'dwb' not in str(rp)                 # replaced wholesale
    assert 'Smac' in out['planner_server']['ros__parameters']['GridBased']['plugin']
    for cm in npar.COSTMAPS:
        assert out[cm][cm]['ros__parameters']['inflation_layer']['inflation_radius'] == 0.40
    # input untouched
    assert BASE['local_costmap']['local_costmap']['ros__parameters']['robot_radius'] == 0.22


def test_required_packages():
    assert npar.required_packages({'controller': 'mppi', 'planner': 'smac2d'}) == [
        'nav2_mppi_controller', 'nav2_smac_planner']
    assert npar.required_packages({'controller': 'dwb'}) == []


def test_bad_inputs_raise():
    for args in (('nope', 'waffle', {}), ('tuned', 'waffle', {'bogus': 1})):
        try:
            npar.resolve_settings(CFG, *args)
        except ValueError:
            continue
        raise AssertionError(f'expected ValueError for {args}')


def test_build_params_file_round_trip(tmp_path=None):
    import tempfile
    d = tempfile.mkdtemp()
    base = os.path.join(d, 'base.yaml')
    yaml.safe_dump(BASE, open(base, 'w'))
    out = npar.build_params_file(base, CFG, 'tuned', 'waffle', {}, os.path.join(d, 'out.yaml'))
    assert yaml.safe_load(open(out))['local_costmap']['local_costmap']['ros__parameters'][
        'inflation_layer']['cost_scaling_factor'] == 4.0
    assert npar.build_params_file(base, CFG, 'default', 'waffle', {}, os.path.join(d, 'x.yaml')) is None
