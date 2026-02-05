# AION Story Engine Python SDK

[![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)](https://github.com/aion-story/sdk-python)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-v6-brightgreen.svg)](https://docs.aion-story.com)

AION Story Engine 的官方 Python SDK，提供简单易用的 API 客户端和命令行工具。

## ✨ 特性

- 🚀 **简单易用** - 直观的 API 和丰富的文档
- 📦 **类型安全** - 使用 Pydantic 模型进行类型验证
- 🐍 **Pythonic** - 符合 Python 习惯的 API 设计
- 🛡️ **健壮性** - 内置错误处理和重试机制
- 🔧 **CLI 工具** - 强大的命令行界面
- 📊 **完整覆盖** - 支持所有 AION API 端点

## 📦 安装

### 使用 pip 安装（推荐）

```bash
pip install aion-sdk
```

### 从源码安装

```bash
git clone https://github.com/aion-story/sdk-python.git
cd sdk-python
pip install -e .
```

### 开发模式安装

```bash
git clone https://github.com/aion-story/sdk-python.git
cd sdk-python
pip install -e ".[dev]"
```

## 🚀 快速开始

### 基础使用

```python
from aion_sdk import AionClient

# 创建客户端
client = AionClient(
    api_key="your_api_key_here",
    base_url="http://localhost:8000/api/v1"
)

# 创建故事会话
session = client.create_session(
    name="我的第一个故事",
    owner_id="user123"
)
print(f"创建会话: {session.session_id}")

# 列出现有会话
sessions = client.list_sessions(limit=10)
for s in sessions:
    print(f"- {s.name} ({s.status})")

# 创建多元宇宙
universe = client.create_universe(
    name="科幻世界",
    creator_id="user123",
    description="充满星际冒险的宇宙",
    physics_rules={"gravity": 9.8, "faster_than_light": True},
    theme="sci-fi",
    tags=["space", "adventure"]
)
print(f"创建宇宙: {universe.universe_id}")
```

### 使用 CLI 工具

```bash
# 安装后会自动安装 aion 命令

# 健康检查
aion health

# 创建会话
aion session create "My Story" --owner user123

# 列出会话
aion session list --limit 10

# 创建宇宙
aion universe create "Sci-Fi World" user123 "A space adventure" sci-fi --tags space,adventure

# 列出资产
aion asset list --limit 20

# 查看市场统计
aion marketplace stats
```

## 📚 详细文档

### 客户端配置

```python
from aion_sdk import AionClient

# 基础配置
client = AionClient(
    api_key="your_api_key",
    base_url="http://localhost:8000/api/v1",
    timeout=30  # 请求超时（秒）
)

# 使用环境变量
import os
client = AionClient(
    api_key=os.getenv("AION_API_KEY"),
    base_url=os.getenv("AION_API_URL", "http://localhost:8000/api/v1")
)
```

### 会话管理

```python
# 创建会话
session = client.create_session(
    name="故事名称",
    owner_id="owner123"
)

# 获取特定会话
session = client.get_session("session-1234")

# 列出会话
sessions = client.list_sessions(
    skip=0,    # 跳过的记录数
    limit=100  # 返回的最大记录数
)
```

### 资产管理

```python
# 列出资产
assets = client.list_assets(
    skip=0,
    limit=100,
    asset_type="world_rule"  # 可选：按类型过滤
)

# 遍历资产
for asset in assets:
    print(f"{asset.name}: ${asset.price:.2f}")
```

### 多元宇宙

```python
# 创建宇宙
universe = client.create_universe(
    name="宇宙名称",
    creator_id="creator123",
    description="宇宙描述",
    physics_rules={
        "gravity": 9.8,
        "thermodynamics": True,
        "magic_system": "mana-based"
    },
    theme="fantasy",
    tags=["magic", "dragons"],
    is_public=True
)

# 列出宇宙
universes = client.list_universes(skip=0, limit=50)
```

### 治理功能

```python
# 列示治理提案
proposals = client.list_proposals(
    skip=0,
    limit=100,
    status="active"  # 可选：按状态过滤
)

for proposal in proposals:
    print(f"{proposal.title}: {proposal.status}")
    print(f"  投票: ✅{proposal.votes_for} / ❌{proposal.votes_against}")
```

### 市场功能

```python
# 获取市场统计
stats = client.get_marketplace_stats()
print(f"总资产: {stats['total_listings']}")
print(f"总收入: ${stats['total_revenue']:,.2f}")

# 列出市场资产
market_assets = client.list_marketplace_assets(skip=0, limit=50)
```

## 🐍 Python 特性

### 类型注解

SDK 完全支持类型注解，可在支持类型检查的 IDE 中获得完整的代码补全和错误检测：

```python
from aion_sdk import Session, Asset, Universe

def process_session(session: Session) -> str:
    return f"Session {session.name} is {session.status}"
```

### 数据类

所有 API 响应都转换为 Python 数据类：

```python
from aion_sdk import Session

session = client.get_session("session-1234")

# 直接访问属性
print(session.session_id)
print(session.name)
print(session.status)

# 转换为字典
data = session.__dict__
# 或者
from dataclasses import asdict
data = asdict(session)
```

### 错误处理

```python
from requests.exceptions import RequestException

try:
    session = client.get_session("invalid-session")
except RequestException as e:
    print(f"请求失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 🛠️ CLI 详细用法

### 全局选项

```bash
aion --api-key your_key --base-url http://localhost:8000/api/v1 --verbose
```

环境变量：
- `AION_API_KEY`: API 密钥
- `AION_API_URL`: API 基础 URL（默认: http://localhost:8000/api/v1）

### 子命令

#### 会话管理

```bash
# 创建会话
aion session create "My Story" --owner user123

# 列出会话
aion session list --skip 0 --limit 100
```

#### 宇宙管理

```bash
# 创建宇宙
aion universe create "Fantasy World" user123 "A magical realm" fantasy \
    --tags magic,dragons \
    --gravity 9.8 \
    --private  # 创建私有宇宙

# 列出宇宙
aion universe list --skip 0 --limit 50
```

#### 资产管理

```bash
# 列出资产
aion asset list --skip 0 --limit 100
```

#### 市场

```bash
# 查看统计
aion marketplace stats
```

#### 治理

```bash
# 列示提案
aion governance list --status active --limit 50
```

## 📊 响应格式

所有响应都经过类型验证，确保数据一致性：

```python
from aion_sdk import Session

session = client.create_session(name="Test")

# 类型安全的属性
session.session_id: str
session.name: str
session.status: str
session.message: Optional[str]
```

## 🔧 高级用法

### 自定义请求

```python
# 如果需要自定义请求，可以使用底层 session
response = client.session.get(
    f"{client.base_url}/custom/endpoint",
    params={"key": "value"}
)
data = response.json()
```

### 批量操作

```python
# 批量创建会话
names = ["Story 1", "Story 2", "Story 3"]
sessions = []
for name in names:
    session = client.create_session(name=name, owner_id="user123")
    sessions.append(session)
    time.sleep(0.1)  # 避免速率限制
```

### 并发请求

```python
import asyncio
import aiohttp

# 使用 aiohttp 进行异步请求
async def fetch_sessions():
    async with aiohttp.ClientSession() as session:
        # 这里需要使用 aiohttp 版本的 SDK
        pass
```

## 📝 示例项目

查看 `examples/` 目录了解更多用法：

- `basic_usage.py` - 基础使用示例
- `batch_operations.py` - 批量操作示例
- `advanced_features.py` - 高级功能示例

## 🧪 测试

运行 SDK 测试：

```bash
# 安装测试依赖
pip install -e ".[test]"

# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=aion_sdk

# 生成 HTML 覆盖率报告
pytest --cov=aion_sdk --cov-report=html
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 开发流程

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📞 支持

- 📖 文档: https://docs.aion-story.com/sdk/python
- 💬 Discord: https://discord.gg/aion-story
- 📧 邮箱: support@aion-story.com
- 🐛 问题反馈: https://github.com/aion-story/sdk-python/issues

## 📦 发布历史

### v6.0.0 (2026-02-05)
- 🎉 初始版本发布
- ✨ 完整的 API 客户端
- ✨ 命令行工具
- ✨ 类型安全的数据类
- ✨ 丰富的文档和示例

---

**AION Story Engine Python SDK** - 让 Python 开发者轻松构建下一代故事应用！
