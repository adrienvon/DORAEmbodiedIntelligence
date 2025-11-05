# DORA 具身智能 - 自动驾驶系统

> 基于 DORA-rs 数据流框架和 CARLA 仿真器的自动驾驶系统。



## 📁 项目结构

```
DORAEmbodiedIntelligence/
├── dora/                      # DORA 框架源码（Rust 工作空间）
│   ├── apis/                  # Python/C/C++ API 绑定
│   ├── binaries/              # CLI、协调器、守护进程
│   ├── examples/              # 示例数据流
│   └── node-hub/              # 预打包节点库（YOLO、相机等）
├── my_autonomous_driver/      # 主自动驾驶应用
│   ├── dataflow.yml           # 数据流配置文件
│   ├── nodes/                 # 自定义节点（网络 I/O）
│   │   ├── receiver_node.py   # CARLA → DORA 桥接
│   │   └── control_node.py    # DORA → CARLA 桥接
│   └── operators/             # 算子（数据处理）
│       └── planner_operator.py # Pure Pursuit 路径跟踪
├── leaderboard/               # CARLA 自动驾驶评估框架
├── scenario_runner/           # 交通场景定义（OpenSCENARIO）
└── py37/                      # Python 虚拟环境（CARLA 依赖）
```


## 🚀 运行说明

### 1️⃣ 安装 DORA 框架

#### Linux
```bash
# 使用一键安装脚本
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/dora-rs/dora/main/install.sh | bash

# 或使用 Cargo 安装
cargo install dora-cli
```

### 2️⃣ 配置 Python 环境

**方式 A: 使用虚拟环境（推荐）**
```bash
# DORA 开发环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install dora-rs pyarrow opencv-python

# CARLA 运行环境
source py37/bin/activate
pip install -r leaderboard/requirements.txt
pip install -r scenario_runner/requirements.txt
```

**方式 B: 使用 Conda**
```bash
conda create -n dora_env python=3.11
conda activate dora_env
pip install dora-rs pyarrow
```

### 3️⃣ 启动 DORA 守护进程

```bash
# 启动协调器和守护进程（必须在运行数据流前执行）
dora up

# 验证状态
dora list
```

### 4️⃣ 运行自动驾驶数据流

```bash
cd my_autonomous_driver

# 构建数据流（首次或修改后）
dora build dataflow.yml

# 启动数据流
dora start dataflow.yml

# 开发模式（支持热重载）
dora start dataflow.yml --attach --hot-reload
```

### 5️⃣ 启动 CARLA 仿真器

**在另一个终端**：
```bash
# 确保 CARLA 0.9.13 已安装
cd /path/to/CARLA_0.9.13
./CarlaUE4.sh

# 或在后台运行无渲染模式
./CarlaUE4.sh -RenderOffScreen
```

### 6️⃣ 运行 Leaderboard 评估

```bash
source py37/bin/activate

export LEADERBOARD_ROOT=$(pwd)/leaderboard
export CARLA_ROOT=/path/to/CARLA_0.9.13
export TEAM_AGENT=leaderboard/autoagents/your_agent.py
export ROUTES=leaderboard/data/routes_devtest.xml

python3 ${LEADERBOARD_ROOT}/leaderboard/leaderboard_evaluator.py \
  --routes=${ROUTES} \
  --agent=${TEAM_AGENT} \
  --track=SENSORS
```

### 7️⃣ 停止所有服务

```bash
# 停止数据流
dora destroy

# 或按 Ctrl+C 停止当前数据流
```

## 🧪 测试说明

### 单元测试

```bash
# 测试所有 Rust 组件
cd dora
cargo test --workspace

# 测试特定包
cargo test -p dora-cli

# 运行基准测试
cargo run --example benchmark --release
```

### 功能测试

```bash
# 测试 DORA 示例数据流
cd dora/examples/python-operator-dataflow
dora up
dora build dataflow.yml
dora start dataflow.yml
```

