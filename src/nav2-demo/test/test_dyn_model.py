import xml.etree.ElementTree as ET

from nav2_demo.dyn_model import Patrol, make_sdf


def test_sdf_is_valid_xml_with_plugin():
    root = ET.fromstring(make_sdf('dyn_walker1'))
    assert root.find('model').get('name') == 'dyn_walker1'
    plugin = root.find('model/plugin')
    assert plugin.get('filename') == 'libgazebo_ros_planar_move.so'
    assert plugin.find('ros/namespace').text == '/dyn_walker1'


def test_patrol_goes_out_and_back():
    p = Patrol((0, 0), (2, 0), speed=0.2)
    vx, vy = p.update(0.0, 0.0)
    assert vx > 0 and vy == 0
    assert p.update(2.0, 0.0) == (0.0, 0.0)      # arrived: flips direction
    vx, _ = p.update(2.0, 0.0)
    assert vx < 0
    assert p.update(0.0, 0.0) == (0.0, 0.0)      # back home: flips again
    assert p.update(0.0, 0.0)[0] > 0


def test_patrol_speed_is_respected():
    p = Patrol((0, 0), (3, 4), speed=0.5)
    vx, vy = p.update(0.0, 0.0)
    assert abs((vx ** 2 + vy ** 2) ** 0.5 - 0.5) < 1e-9
