import os
import tempfile
import xml.etree.ElementTree as ET

from nav2_demo.policy_tools import filter_policy

POLICY = """<?xml version="1.0"?>
<policy version="0.2.0">
  <enclaves>
    <enclave path="/mission_server">
      <profiles><profile ns="/" node="mission_server"><topics publish="ALLOW"><topic>a</topic></topics></profile></profiles>
    </enclave>
    <enclave path="/controller_server">
      <profiles><profile ns="/" node="controller_server"/></profiles>
    </enclave>
    <enclave path="/shared">
      <profiles>
        <profile ns="/" node="dynamic_obstacles"/>
        <profile ns="/" node="planner_server"/>
      </profiles>
    </enclave>
  </enclaves>
</policy>
"""


def test_filter_keeps_only_requested_nodes():
    d = tempfile.mkdtemp()
    src, dst = os.path.join(d, 'in.xml'), os.path.join(d, 'out.xml')
    open(src, 'w').write(POLICY)
    mapping = filter_policy(src, dst, {'mission_server', 'dynamic_obstacles', 'explorer'})
    assert mapping == {'mission_server': '/mission_server', 'dynamic_obstacles': '/shared'}
    root = ET.parse(dst).getroot()
    assert [e.get('path') for e in root.find('enclaves')] == ['/mission_server', '/shared']
    nodes = [p.get('node') for p in root.iter('profile')]
    assert 'planner_server' not in nodes and 'controller_server' not in nodes
