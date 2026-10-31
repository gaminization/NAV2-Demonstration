# Automatic mapping (frontier exploration)

Instead of driving the robot by hand, let it explore and map by itself.

```bash
./scripts/auto_map.sh house          # world name from worlds.yaml
```

What happens:

1. Gazebo starts, Cartographer builds the map, Nav2 (without a saved map) provides driving.
2. The `explorer` node looks for **frontiers** (known free space next to unknown space), picks a good one (near and large), and sends it to Nav2. Repeat.
3. When no reachable frontier remains for a few checks in a row, it saves the map to `~/.nav2_demo/maps/<name>.yaml` and shuts everything down.
4. `scripts/install_map.sh` copies the map into `src/nav2-demo/maps/` and rebuilds, so you can commit it.

Then navigate as usual: `ros2 launch nav2-demo nav2-demo.launch.py world:=house`.

You can also run the launch directly: `ros2 launch nav2-demo nav2-demo.launch.py world:=house mode:=explore` (add `shutdown_on_done:=false` to keep it running afterwards).

## Explorer parameters

Defined in `explorer.py` (override with a params file or by editing defaults):

| Parameter | Default | Meaning |
|---|---|---|
| `start_delay` | 20 s | Wait for Nav2 to become active |
| `min_frontier_size` | 8 cells | Ignore tiny frontiers (noise) |
| `goal_timeout` | 90 s | Give up on a goal and blacklist it |
| `done_after` | 4 | Empty checks in a row before finishing |
| `max_runtime` | 1200 s | Save whatever exists after this long |

## Limits

- Mapping quality depends on Cartographer. Check the saved map (`maps/*.pgm`) visually before relying on it.
- Frontier goals next to walls can be rejected by Nav2 (inflation). The explorer blacklists them and moves on.
- Moving obstacles (`dynamic_obstacles:=true`) will be drawn into the map as smears. Map without them.
- The logic is unit-tested (`test_frontiers.py`), but exploration has not been run live by the author.
