# Security hardening

Context: ROS 2 uses DDS, which by default **broadcasts and accepts traffic from anyone on the same network**, unauthenticated and unencrypted. For a simulation on a laptop the risk is low, but good habits are cheap.

## Level 1: always on (via `scripts/env.sh`)

| Setting | Effect |
|---|---|
| `ROS_LOCALHOST_ONLY=1` | DDS traffic stays on this machine |
| `ROS_DOMAIN_ID=42` | Separates you from other ROS users |

`source scripts/env.sh` in **every** terminal. Terminals with different settings will not see each other (this is a common "why is nothing showing up" cause).

## Level 2: SROS2 (authentication + encryption)

```bash
./scripts/setup_security.sh                       # once: creates ~/.nav2_demo/keystore
source scripts/env.sh secure                      # in every terminal
ros2 launch nav2-demo nav2-demo.launch.py security:=true
```

What this gives you: nodes without the keystore cannot join or read traffic, and traffic is encrypted.

What it does **not** give you:

- All nodes share **one enclave** (`/nav2_demo`), so there is no per-node access control. For that, write a policy and generate one enclave per node (`ros2 security generate_policy`; see the SROS2 docs).
- Gazebo Classic plugins and Nav2 nodes are not guaranteed to all work under SROS2 on every setup. This path is the **least tested** part of the project. If something fails, see Troubleshooting below. Use `ROS_SECURITY_STRATEGY=Permissive` temporarily to tell whether security is the cause.

## Level 3: per-node identities (least privilege)

Shared mode gives every process the same identity. Per-node mode gives **this project's own nodes** (`mission_server`, `dynamic_obstacles`, `explorer`) separate enclaves, each with a permissions policy generated from what the node really does.

```bash
# 1. start the system UNSECURED so the nodes exist
source scripts/env.sh
ros2 launch nav2-demo nav2-demo.launch.py dynamic_obstacles:=true
# 2. another terminal (same env): generate policy + enclaves
./scripts/setup_security_pernode.sh
# 3. stop, then run secured per node
source scripts/env.sh secure
ros2 launch nav2-demo nav2-demo.launch.py security:=true security_mode:=pernode dynamic_obstacles:=true
```

How it works: `ros2 security generate_policy` records what the running nodes publish, subscribe and serve. `policy_filter` keeps only our nodes, then an enclave and permissions are created for each. The launch file starts those nodes with `ROS_SECURITY_ENCLAVE_OVERRIDE` set to their own enclave (mapping in `~/.nav2_demo/enclaves.yaml`). Everything else (Nav2, Gazebo, RViz, bags) stays in the shared enclave.

Limits, honestly:

- Nav2's own nodes are started by Nav2's launch files, so they cannot easily get separate enclaves. Per-node mode covers only this project's nodes.
- A node's policy only allows what it did while the policy was generated. Exercise it first (run a mission, spawn obstacles), then generate.
- Exploration (`explorer`) must be running during generation to be included.
- This depends on SROS2 CLI behaviour that could not be tested here. The policy filtering logic is unit-tested with a sample policy file whose structure may differ slightly from real output.

## Repository hygiene

- `.gitignore` blocks keystores, `*.pem`, `*.key`, bags.
- Never paste tokens into scripts. Use a GitHub personal access token or SSH key for pushing.
- Enable on GitHub: Settings, Code security: private vulnerability reporting, Dependabot alerts, secret scanning.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `could not find enclave` | Run `scripts/setup_security.sh`; ensure the terminal ran `source scripts/env.sh secure` |
| Permission / governance errors | Default enclaves may be too strict for some nodes: generate a policy, or test with `Permissive` |
| Terminal can't see topics | Every terminal must use the same security setting |
