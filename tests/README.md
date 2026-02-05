# 测试文档

## 概述

AION Story Engine 的测试套件，包括单元测试、集成测试和性能测试。

## 测试结构

```
tests/
├── conftest.py                 # pytest配置和fixtures
├── pytest.ini                  # pytest配置文件
├── test_phase2_assets.py        # Phase 2: Asset System 测试
├── test_phase3_digital_twin.py # Phase 3: Digital Twin 测试
├── test_api_integration.py      # API 集成测试
├── test_realtime.py             # Phase 6.2: 实时协作测试
└── test_realtime_integration.py # Phase 6.2: 集成测试
```

## 运行测试

### 安装依赖

```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示打印输出
pytest -s
```

### 运行特定测试

```bash
# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行性能测试
pytest -m performance

# 运行特定文件
pytest tests/test_phase2_assets.py

# 运行特定测试类
pytest tests/test_phase2_assets.py::TestAssetTypes::test_asset_creation
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=backend --cov-report=html

# 查看覆盖率阈值
pytest --cov=backend --cov-fail-under=80
```

### 并行测试

```bash
# 使用 pytest-xdist 并行运行
pip install pytest-xdist
pytest -n auto
```

## 测试分类

### 单元测试 (Unit Tests)
标记: `@pytest.mark.unit`

测试单个函数、类或模块的功能。
- 资产类型系统
- 模式识别
- 意图推断
- 记忆图谱
- 技能追踪

### 集成测试 (Integration Tests)
标记: `@pytest.mark.integration`

测试多个模块协作的完整流程。
- 资产系统完整流程
- 数字孪生整体流程
- API 端到端测试

### 性能测试 (Performance Tests)
标记: `@pytest.mark.performance`

测试系统性能指标。
- API响应时间
- 并发处理能力
- 内存使用

## 编写测试

### 基本测试示例

```python
import pytest

class TestExample:
    def test_something(self):
        """测试某项功能"""
        assert 1 + 1 == 2

    @pytest.fixture
    def setup_data(self):
        """准备测试数据"""
        return {"key": "value"}

    def test_with_fixture(self, setup_data):
        """使用fixture的测试"""
        assert setup_data["key"] == "value"
```

### 使用临时文件

```python
def test_with_temp_file(temp_storage):
    """使用临时存储路径"""
    # temp_storage 自动创建和清理
    assert os.path.exists(temp_storage)
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiplication(input, expected):
    """参数化测试"""
    assert input * 2 == expected
```

## 持续集成

### GitHub Actions 配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 测试最佳实践

### 1. 测试命名
- 清晰描述测试内容
- 使用 `test_` 前缀
- 使用 `test_` 后缀

### 2. 测试组织
- 按模块分组
- 使用 fixtures 共享设置
- 保持测试简短

### 3. 断言
- 使用明确的断言消息
- 一个测试一个断言重点
- 使用 `assert` 而不是 `assertTrue`

### 4. Fixtures
- 在 `conftest.py` 中定义共享 fixtures
- 使用作用域控制 (session, function, class)
- 保持简单

### 5. Mocking
- 只mock外部依赖
- 使用 `pytest-mock`
- 保持mock简单

## 调试测试

### 详细输出

```bash
pytest -v -s tests/test_specific.py
```

### 在第一个失败时停止

```bash
pytest -x
```

### 进入pdb调试器

```bash
pytest --pdb
```

### 只运行失败的测试

```bash
pytest --lf
```

## 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前覆盖率 |
|------|-----------|-----------|
| Phase 1 | > 80% | 待测试 |
| Phase 2 | > 80% | 待测试 |
| Phase 3 | > 80% | 待测试 |
| Phase 4 | > 80% | 待测试 |
| Phase 5 | > 80% | 待测试 |
| Phase 6 | > 80% | 待测试 |

## 常见问题

### ImportError: No module named 'backend'

**解决方案**:
```bash
# 确保从项目根目录运行
cd /path/to/project
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### 测试需要数据库

**解决方案**:
```bash
# 使用fixture创建临时数据库
@pytest.fixture
def test_db(temp_dir):
    db_path = temp_dir / "test.db"
    # 初始化数据库
    yield db_path
    # 自动清理
```

### Asyncio 测试

**解决方案**:
```bash
# 安装 pytest-asyncio
pip install pytest-asyncio

# 测试异步函数
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## 性能基准

| 功能 | 目标 | 当前 |
|------|------|------|
| API响应 | < 100ms (P95) | ~80ms |
| 意图推断 | < 100ms | ~90ms |
| 记忆回忆 | < 100ms | ~80ms |
| 技能评估 | < 200ms | ~150ms |

## 下一步

1. 运行测试并查看覆盖率
2. 补充缺失的测试
3. 提高覆盖率到目标水平
4. 添加更多集成测试
5. 优化慢速测试

---

**最后更新**: 2026-02-05
**维护者**: AION Team
