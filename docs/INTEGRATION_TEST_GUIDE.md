# 首次联调测试指南

**日期**: 2025-10-29  
**阶段**: 第三阶段 - 全系统集成测试  
**目标**: 验证 CARLA + DORA 完整数据流

---

## 🎯 三终端启动流程

### 前置条件检查

运行环境检查脚本：
```bash
./scripts/verify_environment.sh
```

确保所有项都显示 ✅

运行系统状态检查：
```bash
./scripts/start_system.sh
```

---

### 终端 1: 启动 CARLA 服务器 🚗

**目的**: 启动 CARLA 仿真引擎

```bash
# 切换到 CARLA 目录
cd $CARLA_ROOT

# 启动 CARLA 服务器
./CarlaUE4.sh
```

**预期输出**:
```
Waiting for the server to start...
Listening on port 2000
Server ready
```

**验证方法**:
```bash
# 在另一个终端检查端口
nc -z localhost 2000 && echo "✅ CARLA 服务器运行中" || echo "❌ CARLA 未启动"
```

**常见问题**:
- **问题**: `ERROR: ld.so: object 'libXXX.so' cannot be loaded`
  - **解决**: 检查系统库依赖
  
- **问题**: 窗口无法打开
  - **解决**: 确认 X11 或图形界面可用

---

### 终端 2: 启动 DORA 数据流 🔄

**目的**: 启动三个 DORA 节点（sensor_receiver、planner、controller）

```bash
# 切换到项目目录
cd ~/桌面/DORAEmbodiedIntelligence

# 启动 DORA 数据流
./scripts/start_dora.sh
```

**预期输出**:
```
==================================
CARLA-DORA Dataflow Launcher
==================================
Project Root: /home/adrien/桌面/DORAEmbodiedIntelligence
Dataflow Config: /home/adrien/桌面/DORAEmbodiedIntelligence/config/carla_dora_dataflow.yml

Activating uv virtual environment...
Python: /home/adrien/桌面/DORAEmbodiedIntelligence/.venv/bin/python
Python version: Python 3.7.16

Starting DORA dataflow...
Press Ctrl+C to stop

[dora-daemon] Starting...
[sensor_receiver] Starting node...
[SensorReceiver] Listening on localhost:8001
[planner] Starting node...
[SimplePlanner] Initialized
[controller] Starting node...
[VehicleController] Initialized, sending to localhost:8002
```

**验证方法**:
```bash
# 检查 UDP 端口监听
netstat -tuln | grep 8001  # DORA 接收传感器数据
netstat -tuln | grep 8002  # DORA 发送控制指令

# 或使用 ss 命令
ss -tuln | grep -E '8001|8002'
```

**DORA 节点说明**:
1. **sensor_receiver** (dora_nodes/sensors/sensor_receiver.py)
   - 监听 UDP:8001
   - 接收来自 CARLA Agent 的传感器数据
   - 发布到 DORA 数据流: `gps`, `imu`, `speed`, `camera_info`

2. **planner** (dora_nodes/planning/simple_planner.py)
   - 接收: `gps`, `speed`
   - 生成驾驶计划
   - 发布: `plan` (target_speed, target_steering)

3. **controller** (dora_nodes/control/vehicle_controller.py)
   - 接收: `plan`, `speed`
   - PID 控制计算
   - 通过 UDP:8002 发送控制指令到 CARLA

**常见问题**:
- **问题**: `Error: Failed to start daemon`
  - **解决**: 检查是否有旧的 dora 进程
    ```bash
    pkill -f dora
    ./scripts/start_dora.sh
    ```

- **问题**: `ImportError: No module named 'dora'`
  - **解决**: 确认虚拟环境已激活且 dora-rs 已安装
    ```bash
    source .venv/bin/activate
    python -c "import dora"
    ```

---

### 终端 3: 启动 CARLA Agent (Leaderboard) 🎮

**目的**: 启动 CARLA Agent，建立 CARLA ↔ DORA 桥接

```bash
# 切换到项目目录
cd ~/桌面/DORAEmbodiedIntelligence

# 启动 CARLA Agent
./scripts/start_carla_agent.sh
```

**预期输出**:
```
==================================
CARLA Leaderboard Launcher
==================================
Project Root: /home/adrien/桌面/DORAEmbodiedIntelligence
CARLA Root: /home/adrien/桌面/CARLA_Leaderboard_20
Leaderboard Root: /home/adrien/桌面/CARLA_Leaderboard_20
Agent: /home/adrien/桌面/DORAEmbodiedIntelligence/carla_agent/agent_wrapper.py

Starting CARLA Leaderboard...
Routes: /home/adrien/桌面/CARLA_Leaderboard_20/data/AEB_Scenario.xml
Agent: /home/adrien/桌面/DORAEmbodiedIntelligence/carla_agent/agent_wrapper.py

Preparing route...
[CarlaDoraAgent] Agent initialized
[CarlaDoraAgent] Setup with config: /home/adrien/桌面/DORAEmbodiedIntelligence/config/agent_config.json
[DoraUDPBridge] Initialized:
  - Sending sensor data to localhost:8001
  - Receiving control from localhost:8002
Route 1/1: Starting...
```

**数据流验证**:
在终端 2 (DORA) 中应该看到：
```
[SensorReceiver] Received data at step 1
[SimplePlanner] GPS updated: {'latitude': 48.99, 'longitude': 8.00}
[VehicleController] Control: throttle=0.50, steer=0.00, brake=0.00
```

**常见问题**:
- **问题**: `Connection refused: localhost:2000`
  - **解决**: CARLA 服务器未启动，回到终端 1

- **问题**: `ModuleNotFoundError: No module named 'carla'`
  - **解决**: PYTHONPATH 未正确设置
    ```bash
    echo $PYTHONPATH  # 应该包含 carla egg 文件路径
    ```

- **问题**: Agent 启动但 DORA 无数据
  - **解决**: 检查 UDP 通信（见下方调试清单）

---

## 🔍 调试清单

### 1. 网络端口检查

**检查 CARLA 端口**:
```bash
# 方法 1: netcat
nc -z localhost 2000 && echo "✅ CARLA" || echo "❌ CARLA"

# 方法 2: netstat
netstat -tuln | grep 2000

# 方法 3: ss (推荐)
ss -tuln | grep 2000
```

**检查 DORA UDP 端口**:
```bash
# 检查 8001 (CARLA → DORA 传感器数据)
ss -tuln | grep 8001

# 检查 8002 (DORA → CARLA 控制指令)
ss -tuln | grep 8002
```

**预期输出**:
```
tcp   LISTEN 0      5      127.0.0.1:2000       0.0.0.0:*    # CARLA
udp   UNCONN 0      0      127.0.0.1:8001       0.0.0.0:*    # DORA 接收
udp   UNCONN 0      0      127.0.0.1:8002       0.0.0.0:*    # DORA 发送
```

---

### 2. DORA 节点日志检查

DORA 节点的所有 `print()` 输出会显示在终端 2 中。

**正常日志示例**:
```
[SensorReceiver] Received data at step 100
  GPS: lat=48.990, lon=8.002
  Speed: 5.2 m/s
  
[SimplePlanner] Plan generated: target_speed=5.0 m/s, target_steer=0.0

[VehicleController] Control computed:
  Throttle: 0.45
  Steer: 0.00
  Brake: 0.00
```

**异常日志示例**:
```
[SensorReceiver] Error: [Errno 98] Address already in use
# → 解决: 端口被占用，杀死旧进程

[SimplePlanner] No GPS data received
# → 解决: sensor_receiver 未发布 GPS 数据

[VehicleController] Error sending control: [Errno 111] Connection refused
# → 解决: Agent 未监听 8002 端口
```

---

### 3. UDP 通信测试工具

使用项目自带的 UDP 测试脚本：

#### 测试 1: 发送模拟传感器数据到 DORA

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行测试脚本（发送模式）
python scripts/test_udp.py --mode send --port 8001
```

**预期**: 终端 2 (DORA) 中应该看到接收到的数据

#### 测试 2: 监听 DORA 控制指令

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行测试脚本（接收模式）
python scripts/test_udp.py --mode receive --port 8002
```

**预期**: 应该看到来自 DORA controller 的控制消息

#### 测试 3: 完整回路测试

```bash
# 终端 A: 监听 8002
python scripts/test_udp.py --mode receive --port 8002

# 终端 B: 发送到 8001
python scripts/test_udp.py --mode send --port 8001
```

**预期**: 数据流通 → DORA 处理 → 控制指令返回

---

### 4. 常见问题快速诊断

#### 症状: CARLA 窗口显示车辆，但不移动

**可能原因**:
1. Agent 未发送控制指令到 CARLA
2. DORA 控制指令未到达 Agent

**诊断步骤**:
```bash
# 1. 检查 DORA controller 是否发送数据
# 在终端 2 查看是否有 "[VehicleController]" 日志

# 2. 检查 Agent 是否接收控制指令
# 在终端 3 应该看到 "[DoraUDPBridge] Received control: ..."

# 3. 使用 tcpdump 监听 UDP 流量
sudo tcpdump -i lo udp port 8002 -A
```

---

#### 症状: DORA 节点未接收到数据

**可能原因**:
1. Agent 未发送传感器数据
2. 端口绑定失败
3. 防火墙阻止

**诊断步骤**:
```bash
# 1. 检查端口是否被监听
ss -tuln | grep 8001

# 2. 检查 Agent 是否发送数据
# 在终端 3 应该看到 "[DoraUDPBridge] Sending sensor data..."

# 3. 使用 tcpdump 监听
sudo tcpdump -i lo udp port 8001 -A

# 4. 检查防火墙（Debian）
sudo iptables -L -n | grep 8001
```

---

#### 症状: Python 导入错误

**可能原因**:
1. 虚拟环境未激活
2. PYTHONPATH 未设置
3. 包未安装

**诊断步骤**:
```bash
# 1. 确认虚拟环境
which python
# 应该显示: /home/adrien/桌面/DORAEmbodiedIntelligence/.venv/bin/python

# 2. 检查已安装包
pip list | grep -E 'dora|carla|numpy'

# 3. 验证 CARLA egg 文件
echo $PYTHONPATH | grep carla
python -c "import carla; print('✅ CARLA 导入成功')"

# 4. 重新运行环境验证
./scripts/verify_environment.sh
```

---

## 📊 成功验证指标

系统正常运行时，你应该看到：

### 终端 1 (CARLA)
- ✅ 窗口显示 3D 场景
- ✅ 车辆在场景中移动
- ✅ 无错误或警告信息

### 终端 2 (DORA)
- ✅ 三个节点全部启动
- ✅ 定期输出传感器数据日志（约 20Hz）
- ✅ 控制指令计算日志

### 终端 3 (Agent)
- ✅ Agent 初始化成功
- ✅ 传感器数据发送日志
- ✅ 控制指令接收日志
- ✅ Leaderboard 进度显示

### 系统级别
- ✅ 端口 2000、8001、8002 全部活跃
- ✅ 车辆响应 DORA 控制指令
- ✅ AEB 场景正确触发和执行

---

## 🛑 停止系统

**正确的停止顺序**:

1. **终端 3** (Agent): `Ctrl+C`
2. **终端 2** (DORA): `Ctrl+C`
3. **终端 1** (CARLA): `Ctrl+C`

**清理残留进程**:
```bash
# 清理 DORA 进程
pkill -f dora

# 清理 Python 进程
pkill -f "python.*carla"

# 检查端口占用
ss -tuln | grep -E '2000|8001|8002'
```

---

## 📝 测试记录模板

```
测试日期: 2025-10-29
测试人员: [你的名字]
测试场景: AEB (自动紧急制动)

启动顺序:
[ ] 终端 1: CARLA 服务器启动
[ ] 终端 2: DORA 数据流启动
[ ] 终端 3: CARLA Agent 启动

端口检查:
[ ] 2000: CARLA 监听
[ ] 8001: DORA 接收
[ ] 8002: DORA 发送

数据流验证:
[ ] CARLA → DORA 传感器数据
[ ] DORA 规划计算
[ ] DORA 控制计算
[ ] DORA → CARLA 控制指令
[ ] 车辆响应正确

场景测试:
[ ] AEB 触发条件满足
[ ] 车辆成功制动
[ ] 无碰撞发生

问题记录:
[在此记录遇到的问题和解决方法]

结论:
[ ] 测试通过
[ ] 测试失败（原因：_______）
```

---

## 🚀 准备好了吗？

如果所有检查都通过，按照上述三终端启动流程开始你的首次联调测试！

祝测试顺利！🎉
