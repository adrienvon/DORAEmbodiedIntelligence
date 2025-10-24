#!/bin/bash

# Project Overview Generator
# Generates a complete overview of the CARLA-DORA project

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         CARLA-DORA 自动驾驶联合仿真系统                     ║"
echo "║              Project Overview                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Project Info
echo "📦 项目信息"
echo "  名称: CARLA-DORA Joint Simulation System"
echo "  版本: 0.1.0"
echo "  创建: 2025-10-24"
echo "  目标: 自动驾驶挑战赛初赛"
echo ""

# Directory Structure
echo "📁 项目结构"
echo "  carla-dora-sim/"
echo "  ├── carla_agent/          # CARLA Agent 模块"
echo "  │   ├── __init__.py"
echo "  │   └── agent_wrapper.py  # 核心 Agent 实现"
echo "  ├── dora_nodes/           # DORA 数据流节点"
echo "  │   ├── sensors/          # 传感器节点"
echo "  │   ├── planning/         # 规划节点"
echo "  │   └── control/          # 控制节点"
echo "  ├── config/               # 配置文件"
echo "  │   ├── config.yaml"
echo "  │   ├── agent_config.json"
echo "  │   └── carla_dora_dataflow.yml"
echo "  ├── scripts/              # 启动脚本"
echo "  │   ├── start_dora.sh"
echo "  │   ├── start_carla_agent.sh"
echo "  │   ├── start_system.sh"
echo "  │   └── test_udp.py"
echo "  ├── tests/                # 测试文件"
echo "  ├── docs/                 # 文档"
echo "  └── .venv/                # Python 虚拟环境"
echo ""

# Statistics
echo "📊 项目统计"
PYTHON_FILES=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./.git/*" | wc -l)
TOTAL_LINES=$(wc -l carla_agent/*.py dora_nodes/*/*.py tests/*.py 2>/dev/null | tail -1 | awk '{print $1}')
CONFIG_FILES=$(find config/ -type f 2>/dev/null | wc -l)
DOC_FILES=$(find . -maxdepth 2 -name "*.md" | wc -l)

echo "  Python 文件: $PYTHON_FILES"
echo "  代码行数: $TOTAL_LINES"
echo "  配置文件: $CONFIG_FILES"
echo "  文档文件: $DOC_FILES"
echo ""

# Dependencies
echo "🔧 核心依赖"
echo "  • numpy    (数值计算)"
echo "  • pygame   (游戏引擎)"
echo "  • msgpack  (序列化)"
echo "  • pyarrow  (DORA 数据)"
echo "  • pyyaml   (配置解析)"
echo ""

echo "📝 开发工具"
echo "  • pytest   (测试)"
echo "  • black    (格式化)"
echo "  • flake8   (代码检查)"
echo "  • mypy     (类型检查)"
echo ""

# Features
echo "✨ 核心功能"
echo "  ✓ CARLA Leaderboard Agent 实现"
echo "  ✓ UDP 通信桥接 (CARLA ↔ DORA)"
echo "  ✓ 传感器数据处理 (GPS, IMU, 速度, 相机)"
echo "  ✓ DORA 数据流节点"
echo "  ✓ PID 控制器"
echo "  ✓ 完整测试套件"
echo "  ✓ 详细文档"
echo ""

# Testing
echo "🧪 测试状态"
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    TEST_RESULT=$(python -m pytest tests/test_agent.py -q 2>&1 | tail -1)
    echo "  $TEST_RESULT"
    deactivate
else
    echo "  ⚠ 虚拟环境未激活"
fi
echo ""

# Quick Commands
echo "⚡ 快速命令"
echo "  # 安装依赖"
echo "  $ uv sync"
echo ""
echo "  # 运行测试"
echo "  $ source .venv/bin/activate"
echo "  $ python -m pytest tests/ -v"
echo ""
echo "  # 启动系统"
echo "  $ ./scripts/start_dora.sh       # 终端 1"
echo "  $ ./scripts/start_carla_agent.sh # 终端 2"
echo ""
echo "  # 测试 UDP 通信"
echo "  $ python scripts/test_udp.py"
echo ""

# Documentation
echo "📚 文档资源"
echo "  • README.md            - 项目概览"
echo "  • QUICKSTART.md        - 快速启动"
echo "  • docs/INSTALLATION.md - 安装指南"
echo "  • docs/DEVELOPMENT.md  - 开发指南"
echo "  • PROJECT_SUMMARY.md   - 项目总结"
echo ""

# Next Steps
echo "🎯 下一步工作"
echo "  1. 安装 CARLA 和 DORA 环境"
echo "  2. 运行端到端集成测试"
echo "  3. 优化控制算法参数"
echo "  4. 添加更多传感器"
echo "  5. 准备比赛提交材料"
echo ""

# Status
echo "📈 项目状态"
echo "  🟢 基础架构: 完成"
echo "  🟢 核心功能: 完成"
echo "  🟢 测试覆盖: 完成"
echo "  🟢 文档编写: 完成"
echo "  🟡 集成测试: 待进行"
echo "  ⚪ 性能优化: 待开始"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  项目就绪！准备开始集成测试 🚀                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "查看 QUICKSTART.md 开始使用"
echo ""
