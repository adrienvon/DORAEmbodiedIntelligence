# 🎉 欢迎使用 CARLA-DORA 自动驾驶系统

**专为 Debian 12 优化 | 已针对 RTX 3080 Ti 调优**

---

## 👋 您好！

感谢使用 CARLA-DORA 自动驾驶联合仿真系统。我已经为您的 **Debian 12** 系统进行了完整的适配和优化。

### 🖥️ 您的系统配置

```
操作系统: Debian 12.9 (Bookworm)
GPU: NVIDIA GeForce RTX 3080 Ti (12GB VRAM)
驱动版本: 535.247.01
Python: 3.11.2
```

✨ **这是一个强大的配置！** 您可以运行 CARLA 的 Epic 画质模式。

---

## 🚀 立即开始

### 第一步：运行系统诊断

检查您的系统状态：

```bash
./scripts/diagnose_system.sh
```

这将告诉您需要安装什么。

### 第二步：一键安装所有组件

```bash
./scripts/setup_environment_debian.sh
```

选择 **选项 1（完整安装）**，脚本会自动：
- ✅ 安装 CARLA Simulator 0.9.15
- ✅ 安装 DORA Framework
- ✅ 配置 CARLA Leaderboard
- ✅ 设置 Python 虚拟环境
- ✅ 配置所有环境变量

**预计时间**: 15-30 分钟（取决于网络速度）

### 第三步：验证安装

```bash
source ~/.bashrc
./scripts/diagnose_system.sh
```

应该看到 90%+ 的检查通过 ✓

### 第四步：启动系统

```bash
./scripts/start_system.sh
```

---

## 📚 文档导航

根据您的需求选择：

### 🏃 我想快速上手
→ 阅读 [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - 一页式速查表

### 📖 我需要详细的安装说明
→ 阅读 [`docs/DEBIAN_INSTALLATION.md`](docs/DEBIAN_INSTALLATION.md) - Debian 专用完整指南

### 🛠️ 我想了解开发流程
→ 阅读 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - 开发指南

### 🤖 我在使用 AI 编码助手
→ 阅读 [`.github/copilot-instructions.md`](.github/copilot-instructions.md) - AI 助手指南

### 🐛 我遇到了问题
→ 运行 `./scripts/diagnose_system.sh` 获取诊断报告  
→ 查看 [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) 的故障排除部分

---

## 🎯 新增的 Debian 12 特性

### 自动化脚本
- ✨ `scripts/install_carla_debian.sh` - CARLA 一键安装
- ✨ `scripts/install_dora_debian.sh` - DORA 一键安装
- ✨ `scripts/setup_environment_debian.sh` - 完整环境安装向导
- ✨ `scripts/diagnose_system.sh` - 40+ 项系统诊断

### 性能优化
- 🚀 RTX 3080 Ti Epic 画质配置
- �� Vulkan 渲染器优化
- 🚀 UDP 缓冲区优化建议
- 🚀 Python 3.11 原生支持

### 专用文档
- 📖 完整的 Debian 安装指南
- 📖 快速参考卡片
- �� 系统诊断报告
- 📖 更新日志

---

## 💡 专业提示

### RTX 3080 Ti 用户

您的 GPU 非常强大！使用这些参数启动 CARLA：

```bash
cd /opt/carla
./CarlaUE4.sh -quality-level=Epic -benchmark -fps=30 -prefernvidia
```

### 多任务工作流

使用 `tmux` 或 `screen` 管理多个终端：

```bash
# 安装 tmux
sudo apt install tmux

# 创建会话
tmux new -s carla

# 分割窗口
Ctrl+B then %  # 垂直分割
Ctrl+B then "  # 水平分割
```

### 实时监控

```bash
# 监控 GPU
watch -n 1 nvidia-smi

# 或使用更友好的工具
sudo apt install nvtop
nvtop
```

---

## �� 需要帮助？

### 诊断问题

```bash
./scripts/diagnose_system.sh > diagnostic_report.txt
```

然后查看 `diagnostic_report.txt` 了解详情。

### 常见问题

| 问题 | 快速解决 |
|------|---------|
| 找不到 CARLA | `source ~/.bashrc` |
| Import carla 失败 | 检查 `echo $PYTHONPATH` |
| DORA 命令不存在 | `source ~/.cargo/env` |
| 端口被占用 | `pkill -f CarlaUE4` |

详细故障排除请查看 [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)。

---

## 📊 项目状态

当前版本: **0.1.0** (Debian 12 优化版)

- ✅ 核心架构完成
- ✅ UDP 通信正常
- ✅ DORA 数据流就绪
- ✅ 单元测试通过（5/5）
- ✅ Debian 12 完整支持
- ✅ RTX 3080 Ti 优化

查看 [`CHANGELOG.md`](CHANGELOG.md) 了解详细变更。

---

## 🎓 学习路径

### 初学者
1. 安装系统（按上述步骤）
2. 阅读 [`QUICKSTART.md`](QUICKSTART.md)
3. 运行第一个测试
4. 观察数据流动

### 中级用户
1. 阅读 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
2. 修改 `simple_planner.py` 的逻辑
3. 运行测试验证
4. 查看性能指标

### 高级用户
1. 研究 `.github/copilot-instructions.md`
2. 添加新的 DORA 节点
3. 优化控制算法
4. 贡献代码（参考 [`CONTRIBUTING.md`](CONTRIBUTING.md)）

---

## 🔗 有用链接

- [CARLA 官方文档](https://carla.readthedocs.io/)
- [DORA 官方网站](https://dora-rs.ai/)
- [Debian Wiki](https://wiki.debian.org/)
- [项目 GitHub](https://github.com/yourusername/carla-dora-sim)

---

## 🙏 致谢

感谢以下开源项目：
- CARLA Simulator Team
- DORA Framework (dora-rs)
- CARLA Leaderboard
- Debian Project

---

<div align="center">

**准备好开始了吗？**

```bash
./scripts/setup_environment_debian.sh
```

**祝您开发顺利！** 🚗💨

</div>
