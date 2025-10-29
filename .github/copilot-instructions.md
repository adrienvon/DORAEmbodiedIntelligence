# CARLA-DORA 自动驾驶系统 AI 编码指南

## 🚨 项目当前状态 (2025-10-29)

**重大突破**: CARLA 仿真环境已在新硬件（NVIDIA GPU + Debian）上成功启动！

**当前进展**:
- ✅ **硬件升级完成**: 迁移至支持 NVIDIA GPU 的新主机（解除了最大技术障碍）
- ✅ **CARLA 服务器运行中**: `./CarlaUE4.sh` 已启动，端口 2000 监听正常
- ✅ **Leaderboard 框架验证**: `./run_leaderboard.sh` 成功运行，Pygame 窗口显示 "Loading the world"
- ✅ **目标场景确定**: 已切换至 **AEB (自动紧急制动) 场景** (`AEB_Scenario.xml`)
  - 位置: `LEADERBOARD_ROOT/data/AEB_Scenario.xml`
  - 这是具体的、有挑战性的测试场景，为开发提供明确目标

**下一步关键任务** (按优先级):
1. **验证 DORA 环境** - 检查 `dora-cli` 和 `dora-rs` 是否在新主机上正确安装
2. **启动 DORA 数据流** - 运行 `./scripts/start_dora.sh`，确认三个节点正常启动
3. **连接 Bridge** - 运行 `./scripts/start_carla_agent.sh`，建立 UDP 通信链路
4. **端到端测试** - 验证 AEB 场景下的完整数据流（传感器 → 规划 → 控制）

**关键脚本修改记录**:
- `run_leaderboard.sh`: 路线改为 `AEB_Scenario.xml`（不再使用 `routes_devtest.xml`）

**环境配置**:
- Python 环境: Python 3.7.16 (从 Conda py37) + uv 虚拟环境管理
- CARLA Root: 已配置且验证可用
- CARLA 版本: 0.9.14 (egg file: `carla-0.9.14-py3.7-linux-x86_64.egg`)
- Leaderboard/Scenario Runner: 已正确设置
- 虚拟环境: `.venv/` (由 uv 管理，基于 Conda py37 的 Python 3.7.16)

**重要说明 - CARLA Egg 文件与 PYTHONPATH**:
- CARLA Python API 以 `.egg` 文件形式分发，这是一种预编译的二进制包
- ❌ **为什么不能用 uv 管理**: egg 文件不是标准的 PyPI 包，包含编译的 C++ 绑定
- ✅ **解决方案**: 通过 `PYTHONPATH` 环境变量动态加载
- 📍 **配置位置**: `scripts/start_carla_agent.sh` 自动设置正确的 PYTHONPATH
- 🔍 **验证命令**: `PYTHONPATH="$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.14-py3.7-linux-x86_64.egg:$PYTHONPATH" python -c "import carla"`

---

## 系统架构

这是一个自动驾驶联合仿真系统，结合 CARLA Leaderboard 和 DORA 数据流框架：

**三层架构**:
1. **CARLA Simulator**: 高保真仿真环境（端口 2000）
2. **Bridge Layer**: `CarlaDoraAgent` + `DoraUDPBridge` - UDP 通信（端口 8001/8002）
3. **DORA Dataflow**: 分布式数据流处理（sensor_receiver → planner → controller）

**数据流向**: CARLA传感器 → UDP:8001 → DORA处理 → UDP:8002 → CARLA控制

关键文件:
- `carla_agent/agent_wrapper.py`: CARLA Leaderboard API 实现 + UDP bridge
- `config/carla_dora_dataflow.yml`: DORA 节点拓扑定义
- `dora_nodes/{sensors,planning,control}/*.py`: 独立的 DORA 数据流节点

## 开发工作流

### 启动系统（必须按顺序）

**快速检查**:
```bash
./scripts/start_system.sh  # 显示启动指南和环境检查
./scripts/verify_environment.sh  # 验证所有依赖
```

**三终端启动流程**:
```bash
# 终端 1: 启动 CARLA 服务器（必须先启动）
cd $CARLA_ROOT && ./CarlaUE4.sh
# 等待输出: "Listening on port 2000"

# 终端 2: 启动 DORA 数据流
cd ~/桌面/DORAEmbodiedIntelligence
./scripts/start_dora.sh
# 应看到三个节点启动: sensor_receiver, planner, controller
# 所有节点使用统一的 uv 虚拟环境 (.venv)

# 终端 3: 启动 CARLA Agent (Leaderboard + Bridge)
cd ~/桌面/DORAEmbodiedIntelligence
./scripts/start_carla_agent.sh
# 连接到 CARLA，开始 AEB 场景
```

**诊断技巧**: 如果启动失败，检查：
1. **端口状态**: `ss -tuln | grep -E '2000|8001|8002'`
2. **CARLA 连接**: `nc -z localhost 2000 && echo "✅" || echo "❌"`
3. **PYTHONPATH**: `echo $PYTHONPATH | grep carla`
4. **环境变量**: `echo $CARLA_ROOT $LEADERBOARD_ROOT $SCENARIO_RUNNER_ROOT`
5. **虚拟环境**: `which python` 应指向 `.venv/bin/python`

**完整调试指南**: 参见 `docs/INTEGRATION_TEST_GUIDE.md`

### 依赖管理

使用 `uv` (不是 pip/poetry):
```bash
uv sync              # 安装依赖
uv sync --extra dev  # 包含开发依赖（pytest, black, flake8）
uv add <package>     # 添加新依赖
```

虚拟环境位置: `.venv/` (自动创建)

### 测试

```bash
pytest tests/              # 运行所有测试
pytest tests/test_agent.py -v  # 单个文件详细输出
```

**注意**: 集成测试需要 CARLA 服务器运行

## 项目特定约定

### UDP 通信协议

使用 **MessagePack** 序列化（不是 JSON）:

```python
# 发送示例（在 carla_agent/agent_wrapper.py）
sensor_data = {
    'gps': {'latitude': 48.858, 'longitude': 2.294},
    'speed': 10.5,
    'timestamp': time.time()
}
packed = msgpack.packb(sensor_data, use_bin_type=True)
socket.sendto(packed, ('localhost', 8001))

# 接收示例（在 dora_nodes/sensors/sensor_receiver.py）
data, addr = socket.recvfrom(65535)
sensor_data = msgpack.unpackb(data, raw=False)
```

**端口约定**（硬编码在多个文件中）:
- 8001: CARLA → DORA (sensor data)
- 8002: DORA → CARLA (control commands)
- 2000: CARLA simulator RPC port

### DORA 节点开发模式

每个节点是独立的 Python 脚本，遵循模式：

```python
from dora import Node
import pyarrow as pa

def main():
    node = Node()
    
    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            value = event["value"][0].as_py()  # PyArrow 解包
            
            # 处理逻辑...
            result = process(value)
            
            # 发送输出
            node.send_output(
                "output_name", 
                pa.array([result]),  # 必须用 PyArrow 包装
                event["metadata"]["timestamp"]
            )

if __name__ == "__main__":
    main()
```

**关键点**:
- 数据必须用 `pa.array()` 包装
- 使用 `.as_py()` 从 PyArrow 解包
- 节点间通信通过 `carla_dora_dataflow.yml` 定义的 inputs/outputs

### CARLA Agent API

实现 Leaderboard 接口的三个方法（见 `carla_agent/agent_wrapper.py`）:

```python
class CarlaDoraAgent:
    def setup(self, path_to_conf_file: str):
        # 初始化 UDP bridge，读取配置
        
    def sensors(self) -> list:
        # 返回传感器定义列表（GPS, IMU, Speed, Camera）
        # 格式：[{'type': 'sensor.other.gnss', 'id': 'GPS', ...}]
        
    def run_step(self, input_data, timestamp):
        # 1. 提取传感器数据
        # 2. 通过 UDP 发送到 DORA
        # 3. 接收 DORA 控制指令
        # 4. 返回 carla.VehicleControl 对象
```

**传感器数据结构**: 参考 `extract_sensor_data()` 方法，包含 GPS lat/lon、IMU 加速度、速度计和相机元数据。

### 控制指令格式

标准控制消息（DORA → CARLA）:

```python
control = {
    'throttle': 0.5,  # [0.0, 1.0]
    'steer': 0.1,     # [-1.0, 1.0]
    'brake': 0.0      # [0.0, 1.0]
}
```

PID 控制器位于 `dora_nodes/control/vehicle_controller.py`，使用独立的速度和转向 PID。

## 常见修改场景

### 添加新传感器

1. 在 `CarlaDoraAgent.sensors()` 添加定义
2. 在 `CarlaDoraAgent.extract_sensor_data()` 提取数据
3. 在 `sensor_receiver.py` 添加对应的 `node.send_output()`
4. 在 `carla_dora_dataflow.yml` 添加输出声明

### 修改数据流拓扑

编辑 `config/carla_dora_dataflow.yml`:
- `nodes[].id`: 节点标识符
- `nodes[].operator.python`: Python 脚本路径
- `nodes[].inputs`: 格式 `<node_id>/<output_name>`
- `nodes[].outputs`: 输出名称列表

修改后重启 DORA (`./scripts/start_dora.sh`)。

### 调试技巧

**查看 DORA 日志**: 节点的 `print()` 输出会显示在 `dora start` 的终端
**UDP 流量**: 使用 `scripts/test_udp.py` 测试端口连通性
**CARLA 连接**: 检查 `leaderboard_evaluator.py` 的输出是否有 "Connection refused"

## 外部依赖

- **CARLA Python API**: 通过 egg 文件动态加载（版本绑定）
- **DORA**: Rust CLI 工具 + Python 库（`dora-rs`）
- **Leaderboard**: 评估框架，提供路线和场景定义
- **Scenario Runner**: Leaderboard 依赖的场景执行引擎

**PYTHONPATH 设置**: `start_carla_agent.sh` 脚本自动设置，包含 CARLA egg、Leaderboard、Scenario Runner 和项目根目录。

## 代码风格

- **格式化**: 使用 `black` (行宽 100)
- **Linting**: `flake8 --max-line-length=100`
- **文档字符串**: 使用 Google 风格，包含 Args/Returns
- **类型提示**: 使用 `typing` 模块，尤其在公共接口

示例：
```python
def process_data(sensor_data: Dict[str, Any], timeout: float = 0.01) -> Optional[Dict[str, float]]:
    """Process sensor data and return control commands.
    
    Args:
        sensor_data: Dictionary containing GPS, IMU, speed data
        timeout: Socket timeout in seconds
        
    Returns:
        Control commands dict or None if processing fails
    """
```

运行格式化: `black carla_agent/ dora_nodes/ tests/`
