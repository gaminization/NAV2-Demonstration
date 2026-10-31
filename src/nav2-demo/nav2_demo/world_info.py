"""Print one field of a world from worlds.yaml (used by scripts).

    ros2 run nav2-demo world_info house demo_obstacle     ->  "1.0 2.0"
"""
import sys

import os

from .worlds import load_config, resolve


def main():
    if len(sys.argv) != 3:
        print('usage: world_info <world> <key>', file=sys.stderr)
        sys.exit(2)
    world, key = sys.argv[1], sys.argv[2]
    worlds = load_config()['worlds']
    if key == 'map_name' and world in worlds:
        print(os.path.splitext(os.path.basename(resolve(worlds[world]['map'])))[0])
        return
    if world not in worlds or key not in worlds[world]:
        print(f'no key {key!r} for world {world!r}', file=sys.stderr)
        sys.exit(1)
    val = worlds[world][key]
    if isinstance(val, dict) and 'x' in val and 'y' in val:
        print(val['x'], val['y'])
    else:
        print(val)


if __name__ == '__main__':
    main()
