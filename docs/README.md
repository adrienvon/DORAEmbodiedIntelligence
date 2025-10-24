# CARLA-DORA 自动驾驶联合仿真系统

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CARLA](https://img.shields.io/badge/CARLA-0.9.10+-orange.svg)](https://carla.org/)
[![DORA](https://img.shields.io/badge/DORA-latest-green.svg)](https://github.com/dora-rs/dora)

基于 CARLA 仿真器和 DORA 数据流框架的自动驾驶系统，用于自动驾驶挑战赛。

## 📋 项目概述

本项目构建了一个联合仿真系统，结合了：
- **CARLA Leaderboard**: 提供高保真的虚拟环境和传感器数据
- **DORA Platform**: 基于数据流的自动驾驶决策系统

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     CARLA Simulator                          │
│  ┌────────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐   │
│  │   World    │  │ Vehicle │  │ Sensors  │  │ Physics │   │
│  └────────────┘  └─────────┘  └──────────┘  └─────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ UDP (Sensor Data)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    DORA Dataflow                             │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────┐        │
│  │    Sensor    │→ │ Planner  │→ │   Controller   │        │
│  │   Receiver   │  └──────────┘  └────────────────┘        │
│  └──────────────┘                                           │
└────────────────────────┬────────────────────────────────────┘
                         │ UDP (Control Commands)
                         ↓
                  ┌──────────────┐
                  │Vehicle Control│
                  └──────────────┘
```

## 🚀 快速开始

### 环境要求

- **操作系统**: Ubuntu 18.04/20.04/22.04
- **Python**: 3.8.1+
- **CARLA**: 0.9.10+
- **Rust/Cargo**: 最新稳定版 (用于 DORA)
- **工具**: 
  - `uv` (Python 依赖管理)
  - Git

### 1. 安装依赖

#### 安装 uv (Python 依赖管理器)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 安装 CARLA

```bash
# 下载 CARLA (根据你的系统选择版本)
wget https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.13.tar.gz
tar -xzf CARLA_0.9.13.tar.gz -C /opt/carla

# 设置环境变量
echo 'export CARLA_ROOT=/opt/carla' >> ~/.bashrc
source ~/.bashrc
```

#### 安装 CARLA Leaderboard

```bash
git clone https://github.com/carla-simulator/leaderboard.git
git clone https://github.com/carla-simulator/scenario_runner.git

# 设置环境变量
echo 'export LEADERBOARD_ROOT=~/leaderboard' >> ~/.bashrc
echo 'export SCENARIO_RUNNER_ROOT=~/scenario_runner' >> ~/.bashrc
source ~/.bashrc
```

#### 安装 DORA

```bash
# 安装 Rust (如果还没有)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 安装 DORA CLI
cargo install dora-cli

# 安装 DORA Python 包
pip install dora-rs
```

### 2. 克隆并设置项目

```bash
# 克隆项目
git clone <your-repo-url> carla-dora-sim
cd carla-dora-sim

# 使用 uv 安装 Python 依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate
```

### 3. 配置项目

编辑 `scripts/start_carla_agent.sh`，更新 CARLA 路径：

```bash
CARLA_ROOT="/opt/carla"  # 你的 CARLA 安装路径
LEADERBOARD_ROOT="$HOME/leaderboard"  # Leaderboard 路径
SCENARIO_RUNNER_ROOT="$HOME/scenario_runner"  # Scenario Runner 路径
```

### 4. 运行系统

#### 步骤 1: 启动 CARLA 服务器

```bash
cd $CARLA_ROOT
./CarlaUE4.sh
```

等待 CARLA 完全启动（看到 "Listening on port 2000"）

#### 步骤 2: 启动 DORA 数据流

在新终端中：

```bash
cd carla-dora-sim
./scripts/start_dora.sh
```

#### 步骤 3: 启动 CARLA Agent

在另一个新终端中：

```bash
cd carla-dora-sim
./scripts/start_carla_agent.sh
```

#### 或者使用一键启动脚本

```bash
./scripts/start_system.sh
```

## 📁 项目结构

```
carla-dora-sim/
├── carla_agent/              # CARLA Agent 模块
│   ├── __init__.py
│   └── agent_wrapper.py      # Agent 主逻辑 (CARLA ↔ DORA 桥接)
├── dora_nodes/               # DORA 数据流节点
│   ├── sensors/              # 传感器处理节点
│   │   └── sensor_receiver.py
│   ├── planning/             # 规划节点
│   │   └── simple_planner.py
│   └── control/              # 控制节点
│       └── vehicle_controller.py
├── config/                   # 配置文件
│   ├── config.yaml           # 主配置
│   ├── agent_config.json     # Agent 配置
│   └── carla_dora_dataflow.yml  # DORA 数据流定义
├── scripts/                  # 启动脚本
│   ├── start_dora.sh         # 启动 DORA
│   ├── start_carla_agent.sh  # 启动 CARLA Agent
│   └── start_system.sh       # 启动完整系统
├── tests/                    # 测试文件
│   ├── test_agent.py
│   └── test_integration.py
├── docs/                     # 文档目录
├── pyproject.toml            # Python 项目配置 (uv)
└── README.md                 # 本文件
```

## 🔧 技术细节

### 通信协议

系统使用 UDP 进行 CARLA 和 DORA 之间的通信：

- **端口 8001**: CARLA → DORA (传感器数据)
- **端口 8002**: DORA → CARLA (控制指令)
- **序列化**: MessagePack

### 传感器套件

- **GPS**: 位置信息 (纬度、经度、海拔)
- **IMU**: 加速度计、陀螺仪、指南针
- **速度计**: 当前车速
- **摄像头**: RGB 图像 (可选)

### 控制输出

```python
{
    'throttle': 0.0-1.0,  # 油门
    'steer': -1.0-1.0,    # 转向 (-1=左, 1=右)
    'brake': 0.0-1.0      # 刹车
}
```

### DORA 数据流

1. **Sensor Receiver**: 从 CARLA 接收传感器数据
2. **Planner**: 基于传感器数据生成驾驶计划
3. **Controller**: 将计划转换为车辆控制指令

## 🧪 测试

运行单元测试：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_agent.py
```

运行集成测试：

```bash
python -m pytest tests/test_integration.py -v
```

## 📊 性能指标

- **通信延迟**: <10ms (UDP)
- **控制频率**: 20 Hz
- **传感器频率**: 20 Hz

## 🐛 故障排除

### CARLA 连接失败

```bash
# 检查 CARLA 是否在运行
netstat -tuln | grep 2000

# 检查防火墙
sudo ufw allow 2000/tcp
```

### DORA 节点无法启动

```bash
# 检查 Python 路径
which python
echo $PYTHONPATH

# 重新安装 dora-rs
pip install --force-reinstall dora-rs
```

### UDP 通信问题

```bash
# 检查端口是否被占用
netstat -tuln | grep 8001
netstat -tuln | grep 8002

# 测试 UDP 连接
nc -u -l 8001  # 在一个终端
nc -u localhost 8001  # 在另一个终端
```

## 📝 开发指南

### 添加新的传感器

1. 在 `carla_agent/agent_wrapper.py` 的 `sensors()` 方法中添加传感器定义
2. 在 `_extract_sensor_data()` 中添加数据提取逻辑
3. 更新 `dora_nodes/sensors/sensor_receiver.py` 以处理新数据

### 修改控制逻辑

编辑 `dora_nodes/planning/simple_planner.py` 和 `dora_nodes/control/vehicle_controller.py`

### 调整 PID 参数

修改 `config/config.yaml` 中的 PID 参数：

```yaml
control:
  pid:
    speed:
      kp: 0.5  # 比例增益
      ki: 0.1  # 积分增益
      kd: 0.05 # 微分增益
```

## 🎯 路线图

- [x] 基础通信框架
- [x] 传感器数据接收
- [x] 简单控制逻辑
- [ ] 路径规划算法
- [ ] 障碍物检测
- [ ] 高级控制策略
- [ ] 性能优化
- [ ] 完整文档

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📧 联系

- 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)
- 讨论: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🙏 致谢

- [CARLA Simulator](https://carla.org/)
- [DORA-rs Project](https://github.com/dora-rs/dora)
- [CARLA Leaderboard](https://leaderboard.carla.org/)

---

**祝你在挑战赛中取得好成绩！** 🏆
