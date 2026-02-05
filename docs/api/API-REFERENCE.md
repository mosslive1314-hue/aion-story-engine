# AION Story Engine API 文档

## 🌌 API 概述

AION Story Engine API 是一个强大的 RESTful API，用于创建、管理和协作交互式故事世界。

**API 基础 URL**：
- 开发环境：`http://localhost:8000/api/v1`
- 生产环境：`https://api.aion-story.com/api/v1`

## 🔑 认证

API 使用 API Key 进行认证。在请求头中包含您的密钥：

```bash
curl -H "X-API-Key: your_api_key_here" \
     http://localhost:8000/api/v1/sessions
```

### 获取 API Key

1. 注册账户：https://app.aion-story.com/signup
2. 前往仪表板：https://app.aion-story.com/dashboard
3. 创建新的 API Key
4. 复制并安全保存您的密钥

## 📖 API 端点

### 会话管理 (Sessions)

#### 创建会话
```http
POST /api/v1/sessions
Content-Type: application/json
X-API-Key: your_api_key

{
  "name": "My Epic Story",
  "owner_id": "user123"
}
```

**响应示例**：
```json
{
  "session_id": "session-1234",
  "name": "My Epic Story",
  "status": "created",
  "message": "Session created successfully"
}
```

#### 获取会话
```http
GET /api/v1/sessions/{session_id}
X-API-Key: your_api_key
```

**响应示例**：
```json
{
  "session_id": "session-1234",
  "name": "My Epic Story",
  "status": "active",
  "message": "Session retrieved successfully"
}
```

#### 列出会话
```http
GET /api/v1/sessions?skip=0&limit=100
X-API-Key: your_api_key
```

**响应示例**：
```json
{
  "sessions": [
    {
      "session_id": "session-1234",
      "name": "My Epic Story",
      "status": "active",
      "message": "Retrieved successfully"
    }
  ],
  "total": 10
}
```

### 资产管理 (Assets)

#### 获取资产列表
```http
GET /api/v1/assets
X-API-Key: your_api_key
```

**查询参数**：
- `skip` (int): 跳过的记录数（默认：0）
- `limit` (int): 返回的最大记录数（默认：100）
- `asset_type` (string, 可选): 按资产类型过滤

**响应示例**：
```json
{
  "assets": [
    {
      "id": "asset-1",
      "name": "Fire Physics Rule",
      "type": "world_rule",
      "price": 0.0,
      "creator": "alice",
      "rating": 5.0,
      "downloads": 1247
    }
  ],
  "total": 1
}
```

### 创作者市场 (Marketplace)

#### 获取市场统计
```http
GET /api/v1/marketplace/stats
X-API-Key: your_api_key
```

**响应示例**：
```json
{
  "total_listings": 150,
  "total_transactions": 1200,
  "total_revenue": 45000.0
}
```

#### 获取市场资产
```http
GET /api/v1/marketplace/assets
X-API-Key: your_api_key
```

### 多元宇宙 (Universes)

#### 创建宇宙
```http
POST /api/v1/universes
Content-Type: application/json
X-API-Key: your_api_key

{
  "name": "Fantasy World",
  "creator_id": "user123",
  "description": "A magical fantasy universe",
  "physics_rules": {
    "gravity": 9.8,
    "magic_system": "mana-based"
  },
  "theme": "fantasy",
  "tags": ["magic", "dragons", "medieval"],
  "is_public": true
}
```

#### 列出宇宙
```http
GET /api/v1/universes
X-API-Key: your_api_key
```

### 治理 (Governance)

#### 获取提案列表
```http
GET /api/v1/governance/proposals
X-API-Key: your_api_key
```

**查询参数**：
- `skip` (int): 跳过的记录数
- `limit` (int): 返回的最大记录数
- `status` (string, 可选): 按状态过滤（active, passed, rejected）

## 🔄 错误处理

API 使用标准的 HTTP 状态码表示成功或失败：

- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求格式错误
- `401 Unauthorized` - 认证失败
- `403 Forbidden` - 没有权限
- `404 Not Found` - 资源不存在
- `429 Too Many Requests` - 超出速率限制
- `500 Internal Server Error` - 服务器内部错误

### 错误响应格式

```json
{
  "detail": "Error message describing what went wrong"
}
```

## ⏱️ 速率限制

| 计划 | 请求/分钟 | 并发连接 |
|------|----------|----------|
| 免费版 | 100 | 5 |
| 专业版 | 1,000 | 20 |
| 企业版 | 无限制 | 无限制 |

速率限制基于滑动窗口算法。如果超出限制，API 返回 `429 Too Many Requests`。

## 📊 SDK 和库

### Python SDK

```bash
pip install aion-sdk
```

```python
from aion import Client

client = Client(api_key="your_api_key")

# 创建会话
session = client.sessions.create(name="My Story")
print(f"Created session: {session.session_id}")

# 获取资产
assets = client.assets.list()
for asset in assets:
    print(f"{asset.name}: {asset.price}")
```

### JavaScript/TypeScript SDK

```bash
npm install @aion-story/sdk
```

```typescript
import { AionClient } from '@aion-story/sdk';

const client = new AionClient({ apiKey: 'your_api_key' });

// 创建宇宙
const universe = await client.universes.create({
  name: 'My Universe',
  creatorId: 'user123',
  description: 'An amazing universe',
  theme: 'sci-fi',
});
```

## 🧪 测试

### 使用 curl

```bash
# 健康检查
curl http://localhost:8000/health

# 获取会话列表
curl -H "X-API-Key: test_key" \
     http://localhost:8000/api/v1/sessions

# 创建会话
curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-API-Key: test_key" \
     -d '{"name":"Test Story","owner_id":"user123"}' \
     http://localhost:8000/api/v1/sessions
```

### 使用 Postman

1. 下载我们的 Postman 集合：[AION-API-Collection.json](./postman/AION-API-Collection.json)
2. 导入 Postman
3. 设置环境变量：
   - `api_url`: `http://localhost:8000`
   - `api_key`: `your_api_key`
4. 开始测试！

## 📚 示例项目

查看我们的示例项目：

- [Python 示例](https://github.com/aion-story/examples-python)
- [JavaScript 示例](https://github.com/aion-story/examples-js)
- [React 示例](https://github.com/aion-story/examples-react)

## 🆘 支持

- 📖 文档：https://docs.aion-story.com
- 💬 Discord：https://discord.gg/aion-story
- 📧 邮箱：support@aion-story.com
- 🐛 问题反馈：https://github.com/aion-story/engine/issues

## 📄 许可证

本 API 遵循 MIT 许可证。详情请见 [LICENSE](https://github.com/aion-story/engine/blob/main/LICENSE) 文件。

---

**API 版本**: 6.0.0
**最后更新**: 2026-02-05
