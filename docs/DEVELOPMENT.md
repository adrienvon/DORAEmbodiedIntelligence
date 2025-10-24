# 开发指南

本文档提供 CARLA-DORA 项目的开发指南和最佳实践。

## 开发环境设置

### 推荐的 IDE 设置

#### VS Code

推荐扩展:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Rust Analyzer (rust-lang.rust-analyzer)
- YAML (redhat.vscode-yaml)

配置 `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

### 代码风格

#### Python

使用 **Black** 和 **flake8**:

```bash
# 格式化代码
black carla_agent/ dora_nodes/ tests/

# 检查代码质量
flake8 carla_agent/ dora_nodes/ tests/ --max-line-length=100
```

#### 类型提示

使用类型提示提高代码可维护性:

```python
from typing import Dict, List, Optional, Tuple

def process_sensor_data(
    sensor_data: Dict[str, any],
    timestamp: float
) -> Optional[Dict[str, float]]:
    """Process sensor data and return control commands."""
    pass
```

## 项目结构详解

### CARLA Agent 模块

```python
carla_agent/
├── __init__.py           # 模块初始化
└── agent_wrapper.py      # 主 Agent 类
    ├── DoraUDPBridge     # UDP 通信类
    └── CarlaDoraAgent    # CARLA Agent 接口实现
```

**关键方法**:
- `setup()`: 初始化 agent
- `sensors()`: 定义传感器套件
- `run_step()`: 执行一步控制

### DORA 节点模块

```python
dora_nodes/
├── sensors/
│   └── sensor_receiver.py   # 传感器数据接收
├── planning/
│   └── simple_planner.py    # 路径规划
└── control/
    └── vehicle_controller.py # 车辆控制
```

## 添加新功能

### 1. 添加新传感器

**步骤 1**: 在 Agent 中定义传感器

```python
# carla_agent/agent_wrapper.py
def sensors(self) -> list:
    sensors = [
        # ... 现有传感器 ...
        {
            'type': 'sensor.camera.semantic_segmentation',
            'x': 2.0, 'y': 0.0, 'z': 1.4,
            'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
            'width': 800, 'height': 600, 'fov': 100,
            'id': 'SemanticCamera'
        },
    ]
    return sensors
```

**步骤 2**: 提取传感器数据

```python
def _extract_sensor_data(self, input_data: Dict) -> Dict[str, Any]:
    sensor_data = {}
    
    # 添加语义分割相机数据
    if 'SemanticCamera' in input_data:
        camera = input_data['SemanticCamera'][1]
        sensor_data['semantic_camera'] = {
            'width': camera.shape[1],
            'height': camera.shape[0],
            # 可以添加图像处理逻辑
        }
    
    return sensor_data
```

**步骤 3**: 在 DORA 节点中处理数据

```python
# dora_nodes/sensors/sensor_receiver.py
if 'semantic_camera' in sensor_data:
    node.send_output(
        "semantic_camera",
        pa.array([sensor_data['semantic_camera']]),
        sensor_data.get('timestamp', 0)
    )
```

### 2. 创建新的 DORA 节点

**步骤 1**: 创建节点文件

```python
# dora_nodes/perception/object_detector.py
from dora import Node
import pyarrow as pa

def main():
    node = Node()
    
    print("[ObjectDetector] Node started")
    
    for event in node:
        if event["type"] == "INPUT":
            if event["id"] == "camera_data":
                # 处理相机数据
                camera_data = event["value"][0].as_py()
                
                # 执行物体检测逻辑
                detected_objects = detect_objects(camera_data)
                
                # 发送检测结果
                node.send_output(
                    "detected_objects",
                    pa.array([detected_objects]),
                    event["metadata"]["timestamp"]
                )

def detect_objects(camera_data):
    # 实现物体检测逻辑
    return []

if __name__ == "__main__":
    main()
```

**步骤 2**: 更新数据流配置

```yaml
# config/carla_dora_dataflow.yml
nodes:
  # ... 现有节点 ...
  
  - id: object_detector
    operator:
      python: dora_nodes/perception/object_detector.py
      inputs:
        camera_data: sensor_receiver/camera_info
      outputs:
        - detected_objects
    env:
      PYTHONUNBUFFERED: "1"
```

### 3. 实现高级控制算法

**示例: MPC (模型预测控制)**

```python
# dora_nodes/control/mpc_controller.py
import numpy as np
from scipy.optimize import minimize

class MPCController:
    def __init__(self, horizon=10):
        self.horizon = horizon
        self.dt = 0.05  # 50ms
    
    def compute_control(self, state, target_trajectory):
        """
        使用 MPC 计算最优控制
        
        Args:
            state: 当前车辆状态 [x, y, yaw, v]
            target_trajectory: 目标轨迹
            
        Returns:
            控制指令 [acceleration, steering_rate]
        """
        # 定义代价函数
        def cost_function(u):
            # u 是控制序列
            predicted_state = self._predict_trajectory(state, u)
            
            # 计算跟踪误差
            tracking_error = np.sum(
                (predicted_state - target_trajectory) ** 2
            )
            
            # 计算控制平滑度
            control_smoothness = np.sum(np.diff(u) ** 2)
            
            return tracking_error + 0.1 * control_smoothness
        
        # 优化
        u0 = np.zeros(self.horizon * 2)  # 初始猜测
        bounds = [(-3, 3), (-0.5, 0.5)] * self.horizon  # 控制约束
        
        result = minimize(cost_function, u0, bounds=bounds)
        
        # 返回第一个控制指令
        return result.x[:2]
    
    def _predict_trajectory(self, state, u):
        """使用运动学模型预测轨迹"""
        # 实现车辆运动学模型
        pass
```

## 调试技巧

### 1. 日志记录

使用 Python logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.debug("Sensor data received")
logger.info("Control command sent")
logger.warning("High latency detected")
logger.error("Connection lost")
```

### 2. 可视化调试

```python
# 可视化传感器数据
import matplotlib.pyplot as plt

def visualize_sensor_data(sensor_data):
    fig, axes = plt.subplots(2, 2)
    
    # GPS 轨迹
    axes[0, 0].plot(sensor_data['gps_history'])
    axes[0, 0].set_title('GPS Trajectory')
    
    # 速度曲线
    axes[0, 1].plot(sensor_data['speed_history'])
    axes[0, 1].set_title('Speed Profile')
    
    plt.show()
```

### 3. 性能分析

```python
import time
import cProfile

def profile_function(func):
    """性能分析装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {(end-start)*1000:.2f}ms")
        return result
    return wrapper

@profile_function
def expensive_computation():
    # 耗时计算
    pass
```

## 测试

### 单元测试

```python
# tests/test_new_feature.py
import unittest
from your_module import YourClass

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.obj = YourClass()
    
    def test_basic_functionality(self):
        result = self.obj.some_method()
        self.assertEqual(result, expected_value)
    
    def test_edge_case(self):
        with self.assertRaises(ValueError):
            self.obj.some_method(invalid_input)
```

### 集成测试

```bash
# 运行完整测试套件
python -m pytest tests/ -v --cov=carla_agent --cov=dora_nodes
```

## Git 工作流

### 分支策略

- `main`: 稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支

### 提交规范

```bash
# 格式: <type>(<scope>): <subject>

git commit -m "feat(agent): add LiDAR sensor support"
git commit -m "fix(control): correct PID controller parameters"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(agent): add unit tests for sensor extraction"
```

类型:
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

## 性能优化

### 1. 减少通信延迟

```python
# 使用批量发送
def send_batch_data(data_list):
    packed = msgpack.packb(data_list, use_bin_type=True)
    socket.sendto(packed, address)
```

### 2. 优化计算

```python
# 使用 NumPy 向量化
import numpy as np

# 慢
result = [x * 2 for x in data]

# 快
result = np.array(data) * 2
```

### 3. 异步处理

```python
import asyncio

async def process_sensor_data(data):
    # 异步处理传感器数据
    await asyncio.sleep(0)  # 让出控制权
    return processed_data
```

## 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'feat: add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

## 资源

- [CARLA Python API](https://carla.readthedocs.io/en/latest/python_api/)
- [DORA Documentation](https://github.com/dora-rs/dora)
- [PyArrow Documentation](https://arrow.apache.org/docs/python/)
- [MessagePack](https://msgpack.org/)
