# 🚀 AION Story Engine - 快速开始指南

欢迎使用 AION Story Engine！本指南将帮助您快速上手。

## 安装

### 前置要求

- Python 3.12 或更高版本
- pip（Python 包管理器）

### 安装步骤

```bash
# 1. 克隆仓库
git clone <repository-url>
cd story

# 2. 安装项目（开发模式）
pip install -e ".[dev]"

# 3. 验证安装
pytest
```

## 基本概念

### 三层架构

AION Story Engine 采用三层架构：

1. **物理引擎**（Layer 1）- 处理物理规则和世界状态
2. **认知引擎**（Layer 2）- 处理 NPC 决策和行为
3. **叙事引擎**（Layer 3）- 生成故事文本

### 核心组件

- **Blackboard**: 中央数据总线，存储世界状态
- **Session**: 管理一个完整的故事创作会话
- **Node**: 故事中的一个节点（选择点）
- **NodeTree**: 管理分支故事路径

## 快速示例

### 示例 1：创建第一个故事

```python
from aion_engine.session import Session
import tempfile

# 创建会话
with tempfile.TemporaryDirectory() as tmpdir:
    session = Session.create(tmpdir, "实验室冒险")

    # 步骤 1：进入场景
    result1 = session.advance("进入实验室", {"location": "实验室"})
    print(f"场景描述: {result1.narrative}")

    # 步骤 2：触发事件
    result2 = session.advance("打翻酒精瓶并点火", {})
    print(f"场景描述: {result2.narrative}")
    print(f"火灾状态: {result2.world_state.get('fire_active')}")

    # 步骤 3：NPC 响应
    print(f"NPC行动: {result2.npc_actions['isaac'][0]['action']}")

    # 保存会话
    session.save()
```

### 示例 2：探索分支故事

```python
with tempfile.TemporaryDirectory() as tmpdir:
    session = Session.create(tmpdir, "分支测试")

    # 主线：选择灭火
    result1 = session.advance("打翻酒精瓶并点火", {})
    result2 = session.advance("用水灭火", {})
    print(f"结果A: {result2.narrative}")

    # 分支：选择逃跑（需要从之前的节点创建分支）
    # 这需要使用 NodeTree API
    node_tree = session.node_tree
    # TODO: 添加分支创建示例
```

### 示例 3：自定义世界规则

```python
from aion_engine.core.blackboard import Blackboard
from aion_engine.engine import StoryEngine

# 创建自定义故事引擎
engine = StoryEngine()

# 添加自定义世界状态
result = engine.advance(
    "在太空中打开舱门",
    {
        "location": "太空站",
        "air_pressure": 0,
        "fire_active": False
    }
)

print(f"结果: {result.narrative}")
```

## 测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 运行单元测试
pytest tests/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/test_engine.py

# 运行特定测试
pytest tests/test_engine.py::test_full_cycle -v
```

### 代码覆盖率

```bash
# 生成覆盖率报告
pytest --cov=aion_engine --cov-report=html

# 在浏览器中打开 htmlcov/index.html 查看详细报告
```

## 开发和贡献

### 代码格式化

```bash
# 使用 Makefile
make format

# 或手动运行
black aion_engine tests
isort aion_engine tests
```

### 代码检查

```bash
make lint
```

### 添加新功能

1. 编写测试
2. 编写实现
3. 运行测试确保通过
4. 格式化代码
5. 提交

## 常见问题

### Q: 如何添加新的 NPC 类型？

A: 修改 `aion_engine/core/cognition.py` 中的 `_decide_action` 方法。

### Q: 如何修改物理规则？

A: 修改 `aion_engine/core/physics.py` 中的 `process` 方法。

### Q: 如何保存和加载会话？

A: 使用 `Session.save()` 和 `Session.load()` 方法。

## 更多信息

- [完整设计文档](./design/AION-Story-Engine-Design.md)
- [文件管理系统](./design/AION-File-Management-System.md)
- [API 文档](./api/)
- [贡献指南](../README.md#贡献指南)

---

**需要帮助？** 请查看 [GitHub Issues](https://github.com/your-repo/issues) 或联系项目维护者。
