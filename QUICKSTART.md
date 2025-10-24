# 快速启动指南

本指南帮助你快速启动 CARLA-DORA 系统。

## ⚠️ 前置条件

在开始之前，确保已完成：

- ✅ CARLA 已安装并可以运行
- ✅ DORA CLI 已安装 (`dora --version` 可用)
- ✅ 项目依赖已安装 (`uv sync` 已执行)

## 🚀 三步启动

### 第 1 步：启动 CARLA 服务器

打开**终端 1**:

```bash
cd /opt/carla  # 或你的 CARLA 安装路径
./CarlaUE4.sh
```

**等待输出**: `Listening on port 2000`

---

### 第 2 步：启动 DORA 数据流

打开**终端 2**:

```bash
cd ~/carla-dora-sim  # 你的项目路径
./scripts/start_dora.sh
```

**预期输出**:
```
[SensorReceiver] Listening on localhost:8001
[SimplePlanner] Initialized
[VehicleController] Initialized
```

---

### 第 3 步：启动 CARLA Agent

打开**终端 3**:

```bash
cd ~/carla-dora-sim
./scripts/start_carla_agent.sh
```

**预期输出**:
```
[CarlaDoraAgent] Agent initialized
[DoraUDPBridge] Initialized
```

---

## 🎮 验证系统运行

如果一切正常，你应该看到：

1. **CARLA 窗口**: 车辆在场景中自主行驶
2. **DORA 终端**: 定期输出传感器数据接收信息
3. **Agent 终端**: 显示控制指令发送

示例输出:

```
[SensorReceiver] Received data at step 100
[SimplePlanner] GPS updated: {'latitude': 48.858, 'longitude': 2.294}
[VehicleController] Control: throttle=0.50, steer=0.00, brake=0.00
```

## 🛑 停止系统

按顺序停止：

1. **Ctrl+C** 在 Agent 终端 (终端 3)
2. **Ctrl+C** 在 DORA 终端 (终端 2)
3. **Ctrl+C** 在 CARLA 终端 (终端 1)

## 🔧 一键启动 (高级)

使用组合脚本 (需要先手动启动 CARLA):

```bash
# 确保 CARLA 已运行
./scripts/start_system.sh
```

## ⚡ 常见问题快速解决

### ❌ CARLA 未启动

**症状**: `Connection refused on port 2000`

**解决**:
```bash
cd /opt/carla
./CarlaUE4.sh &
sleep 10  # 等待启动
```

### ❌ 端口被占用

**症状**: `Address already in use`

**解决**:
```bash
# 查找并终止占用进程
sudo netstat -tulpn | grep 8001
sudo kill -9 <PID>
```

### ❌ DORA 找不到

**症状**: `dora: command not found`

**解决**:
```bash
source $HOME/.cargo/env
cargo install dora-cli
```

### ❌ Python 模块缺失

**症状**: `ModuleNotFoundError: No module named 'dora'`

**解决**:
```bash
source .venv/bin/activate
uv sync
pip install dora-rs
```

## 📊 监控系统状态

### 检查 UDP 通信

```bash
# 监控端口
watch -n 1 'netstat -u | grep 800'
```

### 查看 DORA 数据流状态

```bash
dora list
```

### 实时日志

```bash
# Agent 日志
tail -f logs/agent.log

# DORA 日志
tail -f logs/dora.log
```

## 🎯 下一步

系统运行后，你可以：

1. **调试参数**: 修改 `config/config.yaml` 中的 PID 参数
2. **添加传感器**: 在 `carla_agent/agent_wrapper.py` 中添加更多传感器
3. **改进算法**: 在 `dora_nodes/planning/` 中实现更复杂的规划逻辑

## 📚 更多资源

- [完整文档](README.md)
- [安装指南](docs/INSTALLATION.md)
- [开发指南](docs/DEVELOPMENT.md)
- [故障排除](docs/TROUBLESHOOTING.md)

---

**祝你测试顺利！** 🎉
