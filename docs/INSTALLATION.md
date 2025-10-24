# 安装指南

本指南将帮助你完整安装 CARLA-DORA 自动驾驶系统。

## 系统要求

### 硬件要求

- **CPU**: Intel i5 或更高 (推荐 i7/Ryzen 7)
- **内存**: 最少 8GB (推荐 16GB+)
- **显卡**: NVIDIA GTX 1060 或更高 (用于 CARLA)
- **存储**: 至少 50GB 可用空间

### 软件要求

- Ubuntu 18.04, 20.04, 或 22.04 LTS
- Python 3.8.1 或更高版本
- CUDA 10.0+ (可选,用于 GPU 加速)

## 详细安装步骤

### 1. 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. 安装基础依赖

```bash
# 安装构建工具
sudo apt install -y build-essential git wget curl

# 安装 Python 开发工具
sudo apt install -y python3 python3-pip python3-dev

# 安装网络工具
sudo apt install -y net-tools netcat
```

### 3. 安装 uv (Python 包管理器)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.bashrc  # 或 source ~/.zshrc
```

### 4. 安装 CARLA

#### 方法 1: 使用预编译版本 (推荐)

```bash
# 创建 CARLA 目录
sudo mkdir -p /opt/carla
cd /tmp

# 下载 CARLA 0.9.13 (或最新版本)
wget https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.13.tar.gz

# 解压
sudo tar -xzf CARLA_0.9.13.tar.gz -C /opt/carla

# 设置权限
sudo chown -R $USER:$USER /opt/carla

# 设置环境变量
echo 'export CARLA_ROOT=/opt/carla' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg' >> ~/.bashrc
source ~/.bashrc
```

#### 方法 2: 从源码编译

参见 [CARLA 官方文档](https://carla.readthedocs.io/en/latest/build_linux/)

### 5. 安装 CARLA Leaderboard 和 Scenario Runner

```bash
# 克隆仓库
cd ~
git clone https://github.com/carla-simulator/leaderboard.git
git clone https://github.com/carla-simulator/scenario_runner.git

# 安装 Leaderboard 依赖
cd ~/leaderboard
pip install -r requirements.txt

# 安装 Scenario Runner 依赖
cd ~/scenario_runner
pip install -r requirements.txt

# 设置环境变量
echo 'export LEADERBOARD_ROOT=~/leaderboard' >> ~/.bashrc
echo 'export SCENARIO_RUNNER_ROOT=~/scenario_runner' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:$LEADERBOARD_ROOT:$SCENARIO_RUNNER_ROOT' >> ~/.bashrc
source ~/.bashrc
```

### 6. 安装 Rust 和 Cargo (用于 DORA)

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 选择默认安装选项 (1)
# 重新加载环境
source $HOME/.cargo/env

# 验证安装
rustc --version
cargo --version
```

### 7. 安装 DORA

```bash
# 安装 DORA CLI
cargo install dora-cli

# 验证安装
dora --version

# 安装 DORA Python 绑定
pip install dora-rs
```

### 8. 克隆和设置项目

```bash
# 克隆项目 (替换为实际 URL)
git clone <your-repo-url> ~/carla-dora-sim
cd ~/carla-dora-sim

# 使用 uv 创建虚拟环境并安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate
```

### 9. 验证安装

#### 测试 CARLA

```bash
# 启动 CARLA 服务器
cd /opt/carla
./CarlaUE4.sh

# 在另一个终端运行测试脚本
cd /opt/carla/PythonAPI/examples
python3 spawn_npc.py
```

如果看到车辆在场景中生成，说明 CARLA 工作正常。

#### 测试 DORA

```bash
# 创建简单的测试数据流
mkdir -p /tmp/dora_test
cd /tmp/dora_test

cat > test_dataflow.yml << 'EOF'
nodes:
  - id: test_node
    operator:
      python: |
        from dora import Node
        node = Node()
        print("DORA is working!")
        for event in node:
            pass
EOF

# 运行测试
dora start test_dataflow.yml
```

### 10. 运行项目测试

```bash
cd ~/carla-dora-sim
source .venv/bin/activate

# 运行单元测试
python -m pytest tests/test_agent.py -v
```

## 常见问题

### CARLA 无法启动

**问题**: `./CarlaUE4.sh` 报错

**解决方案**:
```bash
# 检查显卡驱动
nvidia-smi

# 更新显卡驱动
sudo ubuntu-drivers autoinstall

# 重启系统
sudo reboot
```

### Python 版本冲突

**问题**: Python 版本不兼容

**解决方案**:
```bash
# 安装 pyenv 管理多个 Python 版本
curl https://pyenv.run | bash

# 安装 Python 3.9
pyenv install 3.9.16
pyenv global 3.9.16
```

### DORA 编译失败

**问题**: `cargo install dora-cli` 失败

**解决方案**:
```bash
# 更新 Rust
rustup update

# 安装额外依赖
sudo apt install -y pkg-config libssl-dev

# 重试安装
cargo install dora-cli
```

### 端口被占用

**问题**: UDP 端口 8001/8002 被占用

**解决方案**:
```bash
# 查找占用端口的进程
sudo netstat -tulpn | grep 8001
sudo netstat -tulpn | grep 8002

# 终止进程 (替换 PID)
sudo kill -9 <PID>
```

## 下一步

安装完成后，请查看 [快速开始指南](../README.md#快速开始) 来运行系统。

## 获取帮助

如果遇到问题，请：

1. 查看 [故障排除文档](troubleshooting.md)
2. 在 [GitHub Issues](https://github.com/your-repo/issues) 提问
3. 参考官方文档:
   - [CARLA Documentation](https://carla.readthedocs.io/)
   - [DORA Documentation](https://github.com/dora-rs/dora)
