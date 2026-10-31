"""Filter an SROS2 policy (from `ros2 security generate_policy`) down to chosen nodes.

    policy_filter <all_policy.xml> <out_policy.xml> <node> [<node> ...]

Prints one line per kept enclave:   <node_name> <enclave_path>
"""
import sys
import xml.etree.ElementTree as ET


def filter_policy(in_path, out_path, node_names):
    """Keep only profiles for node_names. Returns {node_name: enclave_path}."""
    tree = ET.parse(in_path)
    root = tree.getroot()
    enclaves = root.find('enclaves')
    mapping = {}
    if enclaves is None:
        raise ValueError('policy has no <enclaves> element')
    for enclave in list(enclaves.findall('enclave')):
        profiles = enclave.find('profiles')
        kept = False
        if profiles is not None:
            for profile in list(profiles.findall('profile')):
                node = profile.get('node')
                if node in node_names:
                    kept = True
                    mapping[node] = enclave.get('path')
                else:
                    profiles.remove(profile)
        if not kept:
            enclaves.remove(enclave)
    tree.write(out_path, encoding='utf-8', xml_declaration=True)
    return mapping


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)
    mapping = filter_policy(sys.argv[1], sys.argv[2], set(sys.argv[3:]))
    missing = set(sys.argv[3:]) - set(mapping)
    for node, path in sorted(mapping.items()):
        print(node, path)
    for node in sorted(missing):
        print(f'warning: node {node!r} was not running when the policy was generated',
              file=sys.stderr)


if __name__ == '__main__':
    main()
