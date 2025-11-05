# DORA Embodied Intelligence - AI Coding Instructions

## Project Overview

This is a **CARLA autonomous driving project** built on the **DORA-rs dataflow framework**. The architecture integrates:
- **DORA-rs**: A Rust-based dataflow framework (10-17x faster than ROS2) for managing robotic pipelines
- **CARLA Simulator**: Provides the driving environment, scenarios, and sensor data
- **Leaderboard**: CARLA's evaluation platform for autonomous driving challenges (see `leaderboard/`)
- **Scenario Runner**: Defines and executes traffic scenarios for testing (see `scenario_runner/`)

The main application (`my_autonomous_driver/`) implements a complete autonomous driving pipeline using DORA's dataflow paradigm.

**Project Structure**:
- `dora/`: DORA framework source code (Rust workspace with Python/C/C++ bindings)
- `my_autonomous_driver/`: Main autonomous driving application
- `leaderboard/`: CARLA evaluation framework
- `scenario_runner/`: Traffic scenario definitions (OpenSCENARIO format)
- `py37/`: Python virtual environment (for CARLA/leaderboard dependencies)

## Architecture: DORA Dataflow Paradigm

### Core Concepts

DORA uses a **declarative YAML-based dataflow** where computation is split into isolated processes:

1. **Nodes** (`custom:`): Standalone processes with network I/O or complex logic. Define main entry point.
2. **Operators** (`operator:`): Lightweight Python/Rust classes with `on_event()` method for data transformations
3. **Connections**: Explicit input/output declarations creating a directed acyclic graph (DAG)

**Key Pattern**: `dataflow.yml` is the source of truth. All data flows are explicitly declared.

### Example from `my_autonomous_driver/dataflow.yml`:

```yaml
nodes:
  - id: receiver_node
    custom:
      source: nodes/receiver_node.py    # Standalone process
    outputs:
      - gnss_data
  
  - id: planner_operator
    operator:
      python: operators/planner_operator.py  # Lightweight transform
      inputs:
        gnss_data: receiver_node/gnss_data
      outputs:
        - control_cmd
```

**Data Flow**: CARLA → `receiver_node` → `planner_operator` → `control_node` → CARLA Agent

## Critical Developer Workflows

### Python Environment Setup

**Important**: DORA Python nodes and CARLA require different Python environments:

```bash
# For DORA examples and development
python3 -m venv .venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
pip install dora-rs pyarrow opencv-python

# For CARLA/Leaderboard (uses py37/ directory)
source py37/bin/activate
pip install -r leaderboard/requirements.txt
pip install -r scenario_runner/requirements.txt
```

**Conda Alternative**: DORA supports conda environments. Specify in `dataflow.yml`:
```yaml
nodes:
  - id: my_node
    operator:
      python: my_operator.py
      conda_env: my_env  # Uses named conda environment
```

### Running DORA Dataflows

```bash
# 1. Start DORA daemon and coordinator (REQUIRED before any dataflow)
dora up

# 2. Build the dataflow (compiles Rust nodes if needed)
dora build dataflow.yml

# 3. Start the dataflow
dora start dataflow.yml

# Hot-reloading Python nodes during development:
dora start dataflow.yml --attach --hot-reload
```

**Important**: `dora up` is a prerequisite. Without it, dataflows fail silently. It starts:
- **Coordinator**: Orchestrates dataflow execution
- **Daemon**: Manages node processes and inter-process communication

**Management Commands**:
```bash
dora list      # List running dataflows
dora destroy   # Stop all dataflows
dora daemon    # Manually start daemon (usually done by `dora up`)
```

### CARLA Integration Workflow

This project bridges DORA and CARLA via **network sockets**:
1. **CARLA** → UDP/TCP → **receiver_node** (converts to DORA messages)
2. **DORA operators** process data (e.g., path planning)
3. **control_node** → UDP → **CARLA agent** (converts from DORA messages)

**Version Compatibility**: CARLA Leaderboard and ScenarioRunner versions MUST match. Check `scenario_runner/CARLA_VER` and leaderboard docs.

**Running CARLA Leaderboard**:
```bash
# 1. Activate CARLA environment
source py37/bin/activate

# 2. Set environment variables (see leaderboard/run_leaderboard.sh)
export LEADERBOARD_ROOT=/path/to/leaderboard
export CARLA_ROOT=/path/to/CARLA_0.9.x
export TEAM_AGENT=leaderboard/autoagents/your_agent.py
export ROUTES=leaderboard/data/routes_devtest.xml

# 3. Run evaluation
python3 ${LEADERBOARD_ROOT}/leaderboard/leaderboard_evaluator.py \
  --routes=${ROUTES} \
  --agent=${TEAM_AGENT} \
  --track=SENSORS
```

**Sensor Dependencies**: Leaderboard requires specific packages in `py37/`:
- `dictor`, `requests` - API communication
- `opencv-python==4.2.0.32` - Specific version for CARLA compatibility
- `pygame`, `tabulate`, `pexpect` - Simulation control
- `transforms3d` - Coordinate transformations

### Building & Testing

```bash
# Rust workspace (dora/)
cargo build --workspace          # Build all
cargo test --workspace           # Run tests
cargo build -p dora-cli          # Build specific package

# Python dataflows
cd dora/examples/python-operator-dataflow
dora up && dora start dataflow.yml
```

**CI Note**: GitHub Actions runs tests on Linux/Windows/macOS. See `dora/CONTRIBUTING.md` for CI details.

## Project-Specific Conventions

### DORA Message Format: Apache Arrow

All inter-node communication uses **PyArrow** arrays, not native Python types:

```python
import pyarrow as pa

# ✓ Correct - use PyArrow
send_output("bbox", pa.array(arrays.ravel()), metadata)

# ✗ Wrong - don't use native types
send_output("bbox", arrays.tolist(), metadata)  # Will fail
```

**Why Arrow**: Zero-copy serialization for extreme performance. No pickle/JSON overhead.

### Python Operator Pattern

All Python operators MUST implement this exact class structure:

```python
from dora import DoraStatus

class Operator:
    def on_event(self, dora_event, send_output) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            input_id = dora_event["id"]
            value = dora_event["value"]  # Already a PyArrow array
            metadata = dora_event["metadata"]
            
            # Process and send output
            result = process(value.to_numpy())
            send_output("output_name", pa.array(result), metadata)
        
        return DoraStatus.CONTINUE
```

### Custom Node Pattern (Standalone Processes)

For nodes with complex I/O (e.g., `receiver_node.py` with socket servers):

```python
from dora import Node

def main():
    node = Node()
    
    for event in node:
        if event["type"] == "INPUT":
            # Process tick events, trigger outputs
            node.send_output("gnss_data", pa.array(data), metadata)
```

**Key Difference**: Custom nodes manage their own event loop, operators are callbacks.

### Naming Conventions

- **dataflow.yml node IDs**: `snake_case` (e.g., `receiver_node`, `planner_operator`)
- **Output names**: `snake_case` (e.g., `gnss_data`, `control_cmd`)
- **File structure**: `nodes/` for custom nodes, `operators/` for operators
- **Rust packages**: `kebab-case` in `Cargo.toml` (e.g., `dora-node-api`)

### CARLA-Specific Patterns

**Coordinate Systems**: CARLA uses right-handed Z-up coordinates. Transform carefully when interfacing with other frameworks (ROS2 uses X-forward).

**Sensor Data**: 
- GNSS: JSON `{"lat": float, "lon": float, "alt": float}`
- IMU: JSON `{"accel": [x,y,z], "gyro": [x,y,z]}`
- LiDAR: Raw binary point cloud (needs parsing)

## Integration Points & Dependencies

### DORA ↔ CARLA Bridge

- **Receiver Node** (`my_autonomous_driver/nodes/receiver_node.py`): UDP server on port 12345 (GNSS/IMU), TCP server on port 5005 (LiDAR)
- **Control Node** (`my_autonomous_driver/nodes/control_node.py`): UDP client to 192.168.1.1:23456

**Thread Safety**: `SensorDataBuffer` class uses locks. Always follow the pattern in `receiver_node.py`.

### Pre-packaged Node Hub

`dora/node-hub/` contains reusable nodes (yolo, microphone, video-capture, etc.). Reference them in dataflows:

```yaml
nodes:
  - id: camera
    path: opencv-video-capture  # No .py extension, uses node-hub
```

### ROS2 Bridge (Experimental)

Enable ROS2 integration via `dora-ros2-bridge`. See `dora/examples/python-ros2-dataflow/` for usage patterns.

## Key Files & Directories

- **`dora/Cargo.toml`**: Workspace manifest. Version = 0.3.8 across all crates.
- **`dora/binaries/cli/`**: Source for `dora` command-line tool
- **`dora/apis/python/`**: Python bindings (node and operator APIs)
- **`dora/examples/`**: Reference implementations (python-operator-dataflow is the canonical example)
- **`my_autonomous_driver/dataflow.yml`**: Main autonomous driving pipeline
- **`leaderboard/leaderboard/leaderboard_evaluator.py`**: CARLA evaluation harness
- **`scenario_runner/`**: CARLA scenario definitions (OpenSCENARIO format)

## Common Pitfalls

1. **Forgot `dora up`**: Dataflows hang indefinitely. Always run first.
2. **Mixing data types**: Always use PyArrow arrays, never native Python lists/dicts in outputs.
3. **Operator vs Node confusion**: Use operators for pure data transforms, nodes for I/O-heavy tasks.
4. **CARLA version mismatch**: Leaderboard/ScenarioRunner versions must align. Check tags.
5. **Missing build step**: Rust nodes need `cargo build` before `dora start`. Use `build:` in YAML.
6. **Metadata propagation**: Always pass `metadata` through in operators: `send_output(..., metadata)`.

## Testing & Debugging

```bash
# Check DORA daemon status
dora list

# Stop all dataflows
dora destroy

# View logs with OpenTelemetry (if configured)
# Logs go to stdout by default
```

**Hot-reload demo**: [Watch code changes live](http://www.youtube.com/watch?v=NvvTEP8Jak8)

**Debugging Tips**:
- Use `send_stdout_as: stdout` in operator config to capture print statements as DORA outputs
- Always check `dora list` first when dataflows don't start - daemon may not be running
- For network issues, verify ports 12345 (UDP), 5005 (TCP), 23456 (UDP) are available
- Check Python interpreter with `which python` to ensure correct venv is activated

**Common Test Patterns**:
```bash
# Run all Rust tests
cd dora && cargo test --workspace

# Test specific package
cargo test -p dora-cli

# Test Python operator locally before integration
python3 operators/planner_operator.py  # Won't work - needs DORA runtime

# Instead, use minimal dataflow for testing
dora start test_dataflow.yml --hot-reload
```

## References

- DORA Documentation: https://dora-rs.ai/docs/guides/
- CARLA Leaderboard: https://leaderboard.carla.org/
- Apache Arrow: https://arrow.apache.org/docs/python/
- Contributing: `dora/CONTRIBUTING.md`
