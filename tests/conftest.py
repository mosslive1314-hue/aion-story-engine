"""
Pytest Configuration
测试配置和共享fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return Path(__file__).parent


@pytest.fixture(scope="function")
def temp_dir():
    """临时目录"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # 清理
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_storage(temp_dir):
    """临时存储文件"""
    storage_path = temp_dir / "test_storage.json"
    yield str(storage_path)


@pytest.fixture(scope="session")
def sample_data():
    """示例数据"""
    return {
        "story": {
            "id": "story-1",
            "name": "Test Story",
            "description": "A test story"
        },
        "user": {
            "id": "user-1",
            "name": "Test User",
            "email": "test@example.com"
        },
        "node": {
            "id": "node-1",
            "type": "scene",
            "title": "Chapter 1",
            "content": "Once upon a time..."
        }
    }


@pytest.fixture(scope="session")
def mock_ai_responses():
    """模拟AI响应"""
    return {
        "suggestion": "This is a suggested continuation",
        "correction": "Here's a better version",
        "completion": "Auto-completed text"
    }


# 测试标记
pytestmark.unit = pytest.mark.unit
pytestmark.integration = pytest.mark.integration
pytestmark.performance = pytest.mark.performance
pytestmark.slow = pytest.mark.slow


# 配置
def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests"
    )


def pytest_collection_modifyitems(session, config, items):
    """测试收集修改"""
    # 默认跳过性能测试
    # 运行性能测试: pytest -m performance
    if not config.getoption("-m"):
        skip_performance = pytest.mark.skip("Skipping performance tests (use -m performance to run)")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)
