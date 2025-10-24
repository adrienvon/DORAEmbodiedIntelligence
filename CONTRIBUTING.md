# 贡献指南

感谢你对 CARLA-DORA 项目的兴趣！

## 如何贡献

### 报告问题

如果你发现 bug 或有功能建议：

1. 检查 [Issues](https://github.com/your-repo/issues) 是否已存在类似问题
2. 创建新 Issue，包含：
   - 清晰的标题
   - 详细的描述
   - 复现步骤（如果是 bug）
   - 预期行为 vs 实际行为
   - 环境信息（OS, Python 版本等）

### 提交代码

1. **Fork 项目**
   ```bash
   # 在 GitHub 上点击 Fork
   git clone https://github.com/YOUR_USERNAME/carla-dora-sim.git
   cd carla-dora-sim
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **设置开发环境**
   ```bash
   uv sync --extra dev
   source .venv/bin/activate
   ```

4. **编写代码**
   - 遵循代码风格（使用 black 和 flake8）
   - 添加必要的注释和文档字符串
   - 编写测试用例

5. **运行测试**
   ```bash
   # 格式化代码
   black carla_agent/ dora_nodes/ tests/
   
   # 检查代码质量
   flake8 carla_agent/ dora_nodes/ tests/ --max-line-length=100
   
   # 运行测试
   pytest tests/ -v
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   提交信息格式：
   - `feat:` 新功能
   - `fix:` bug 修复
   - `docs:` 文档更新
   - `style:` 代码格式
   - `refactor:` 重构
   - `test:` 测试
   - `chore:` 构建/工具

7. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   然后在 GitHub 上创建 Pull Request。

## 代码风格

### Python

- 使用 **Black** 格式化（行长度 100）
- 遵循 **PEP 8** 规范
- 使用类型提示
- 添加文档字符串

示例：
```python
def process_data(
    sensor_data: Dict[str, Any],
    timestamp: float
) -> Optional[Dict[str, float]]:
    """
    Process sensor data and generate control commands.
    
    Args:
        sensor_data: Dictionary containing sensor readings
        timestamp: Current timestamp in seconds
        
    Returns:
        Control commands or None if processing fails
        
    Raises:
        ValueError: If sensor_data is invalid
    """
    # Implementation
    pass
```

### 注释

- 使用清晰、简洁的注释
- 解释"为什么"，而不是"做什么"
- 复杂逻辑必须添加注释

## 测试要求

所有新功能必须包含测试：

```python
# tests/test_new_feature.py
import unittest
from your_module import YourClass

class TestNewFeature(unittest.TestCase):
    def test_basic_case(self):
        """Test basic functionality"""
        obj = YourClass()
        result = obj.method()
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        """Test edge case handling"""
        # Test implementation
        pass
```

## 文档要求

更新相关文档：

1. **代码文档**: 添加/更新文档字符串
2. **README**: 如果添加了新功能
3. **开发指南**: 如果改变了开发流程
4. **API 文档**: 如果修改了接口

## PR 检查清单

在提交 PR 之前，确保：

- [ ] 代码已格式化（black）
- [ ] 通过代码检查（flake8）
- [ ] 所有测试通过
- [ ] 添加了新测试（如果适用）
- [ ] 更新了文档
- [ ] 提交信息清晰
- [ ] 没有不相关的更改

## 开发流程

1. 选择一个 Issue 或创建新的
2. 在 Issue 中评论表示你要处理它
3. Fork 并创建分支
4. 实现功能/修复
5. 提交 PR
6. 等待审核
7. 根据反馈修改
8. 合并！

## 需要帮助？

- 查看 [开发指南](docs/DEVELOPMENT.md)
- 在 Issue 中提问
- 加入讨论

感谢你的贡献！🎉
