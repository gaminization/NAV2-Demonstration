# QoS (Quality of Service) settings

QoS decides how DDS delivers messages. A **publisher and subscriber with incompatible QoS silently do not connect**, a very common beginner problem.

## Profiles used here (`nav2_demo/qos.py`)

| Profile | Reliability | Durability | Depth | Used for |
|---|---|---|---|---|
| `RELIABLE` | reliable | volatile | 10 | commands and events |
| `LATCHED` | reliable | transient_local | 1 | "last value" topics: `/mission_status`, `/initialpose` |
| `SENSOR` | best_effort | volatile | 5 | high-rate sensors like `/scan` (reference profile) |

Compatibility rule: the publisher must offer at least what the subscriber requests. Reliable beats best-effort, transient_local beats volatile. That is why `/initialpose` is published latched: it works for both volatile and latched subscribers.

## Topic overview (recorded in bags)

| Topic | Typical QoS |
|---|---|
| `/scan` | best_effort |
| `/odom`, `/tf` | reliable / best_effort depending on publisher |
| `/map`, `/tf_static`, `/amcl_pose` | reliable, transient_local |
| `/cmd_vel` | reliable |

Check any topic yourself:

```bash
ros2 topic info /scan --verbose
```

## Bag recording

`config/qos/bag_qos_overrides.yaml` pins the QoS the recorder uses, so latched topics like `/map` are captured even if the recorder starts late. Passed to `ros2 bag record --qos-profile-overrides-path`.

## Debug tips

- No data on `ros2 topic echo /scan`? Add `--qos-reliability best_effort`.
- RViz shows no map? Set the Map display's *Durability* to *Transient Local*.
