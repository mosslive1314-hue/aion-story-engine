# 🌌 AION Story Engine

**想象力的基础设施**

AION Story Engine 是一个基于世界模型的多层叙事系统，结合了 Medici Synapse 跨域创新引擎和创作者数字孪生系统。

## 🎉 Phase 6.2: 实时协作系统 (最新)

### ✨ 新功能亮点

**实时协作编辑系统** - 支持多用户同时编辑、实时同步、冲突解决！

#### 🚀 核心功能
- ✅ **实时协作编辑** - 多用户同时编辑同一文档
- ✅ **操作变换 (OT)** - 智能处理并发编辑冲突
- ✅ **Presence系统** - 心跳监控、会话追踪、参与度评分
- ✅ **通知系统** - 多通道通知、模板系统
- ✅ **撤销/重做** - 完整历史操作支持
- ✅ **分支管理** - 文档分支创建和合并
- ✅ **快照系统** - 快速创建和恢复版本

#### 📊 测试报告
```
✅ 总测试数: 67个 (100% 通过)
✅ 单元测试: 43个
✅ 集成测试: 24个
✅ 性能测试: 全部通过
```

#### 🚀 快速开始
```bash
# 1. 启动WebSocket服务器
python -m aion_engine.realtime.websocket

# 2. 启动前端应用
cd frontend && npm install && npm run dev

# 3. 访问编辑器
http://localhost:3000/editor

# 4. 或使用测试客户端
node test_client.js ws://localhost:8765 demo-doc user1 "张三"
```

#### 📚 文档
- **[Phase 6.2 完整总结](./docs/developer/Phase-6-2-Complete-Summary.md)** - 详细的系统总结
- **[实时协作系统指南](./docs/developer/Realtime-Collaboration-System.md)** - 架构和API
- **[编辑器使用指南](./docs/developer/Realtime-Editor-Guide.md)** - 前端开发指南

---

## 📋 项目文档

- **[完整设计文档](./docs/design/AION-Story-Engine-Design.md)** - 系统的完整设计
- **[文件管理系统](./docs/design/AION-File-Management-System.md)** - 文件组织和管理规范

## 🎯 核心特性

### 三层世界模拟架构

1. **Layer 1: 物理引擎** - 物质守恒、热力学、因果推理
2. **Layer 2: 认知引擎** - NPC独立推理、伪信念、记忆系统
3. **Layer 3: 叙事引擎** - 时间线预测、反事实模拟

### Medici Synapse 融合

- 跨域创新引擎
- 结构同构性映射
- 强制跨界创新
- 完整的创新提案

### 创作者数字孪生

- 个人创作画像
- 意图推理引擎
- 创作记忆图谱
- 智能建议系统

### 资产积累平台

- 可复用的创作资产
- 智能组合推荐
- 资产交易市场
- 创作者经济

### 节点管理系统

- 分支时间线
- 无限分支探索
- 分支对比与合并
- 时间线折叠预测

## 🚀 快速开始

### 安装

```bash
git clone <repository-url>
cd story
pip install -e ".[dev]"
```

### 使用示例

```python
from aion_engine.session import Session
import tempfile

# 创建一个新的会话
with tempfile.TemporaryDirectory() as tmpdir:
    session = Session.create(tmpdir, "我的故事")

    # 推进故事
    result = session.advance("进入实验室", {"location": "实验室"})
    print(result.narrative)
    # 输出: "艾萨克在实验室中工作。"

    # 继续故事，触发火灾
    result = session.advance("打翻酒精瓶并点火", {})
    print(result.narrative)
    # 输出: "艾萨克注意到植物开始燃烧，表情变得严肃。"
    print(f"火灾状态: {result.world_state.get('fire_active')}")
    # 输出: "火灾状态: True"

    # NPC 反应
    print(f"NPC行动: {result.npc_actions['isaac'][0]['action']}")
    # 输出: "NPC行动: prioritize_notes"

    # 保存会话
    session.save()
```

## 🚀 实现路线图

### Phase 1: MVP（已完成）
- [x] 核心三层引擎
- [x] 节点树管理
- [x] 本地文件系统
- [x] 测试用例

### Phase 2: 资产系统（已完成）
- [x] 抽象层引擎
- [x] 资产沉淀机制
- [x] Medici Synapse集成
- [x] 基础个人画像

### Phase 3: 数字孪生（已完成）
- [x] 完整个人画像
- [x] 意图推理
- [x] 智能建议
- [x] 记忆图谱

### Phase 4: 协作与市场（已完成）
- [x] 多人协作
- [x] 资产市场
- [x] 云端同步
- [x] Web界面

### Phase 5: 大规模宇宙（已完成）
- [x] 多元宇宙架构
- [x] DAO治理
- [x] 创作者经济
- [x] 完整生态

### Phase 6: 开发者生态（已完成）
- [x] API设计
- [x] SDK开发
- [x] CLI工具

### Phase 6.1: 开发者工具（已完成）
- [x] FastAPI应用
- [x] API文档
- [x] CLI工具
- [x] SDK封装

### Phase 6.2: 实时协作系统（已完成）⭐
- [x] WebSocket服务器
- [x] 同步引擎
- [x] Presence API
- [x] 通知系统
- [x] 实时编辑器
- [x] 集成测试

### Phase 6.3: 高级编辑器（规划中）
- [ ] 富文本编辑
- [ ] 节点可视化
- [ ] 多媒体支持
- [ ] 语音输入

### Phase 6.4: 性能与扩展（规划中）
- [ ] 数据库优化
- [ ] Redis集成
- [ ] 异步处理
- [ ] 微服务架构

### Phase 6.5: AI增强（规划中）
- [ ] LLM写作助手
- [ ] 智能内容补全
- [ ] 内容审核
- [ ] 自动摘要

## 🛠️ 技术栈

- **语言**: Python 3.12+
- **框架**: FastAPI, Pydantic
- **存储**: JSON + SQLite + Redis
- **AI集成**: Claude, GPT-4o, Chroma
- **前端**: CLI (Rich/Typer), Web (Next.js)

## 📁 文件结构

```
aion-engine/
├── 📂 aion_engine/
│   ├── 📂 realtime/          # Phase 6.2 实时协作系统
│   │   ├── sync.py           # 同步引擎 (467行)
│   │   ├── presence.py       # Presence API (1011行)
│   │   ├── notifications.py # 通知系统 (202行)
│   │   └── websocket.py     # WebSocket服务器 (186行)
│   │
│   ├── 📂 api/              # FastAPI应用
│   ├── 📂 cli/               # CLI工具
│   ├── 📂 core/              # 核心引擎
│   ├── 📂 multiverse/        # 多元宇宙
│   ├── 📂 governance/        # DAO治理
│   └── 📂 session.py         # 会话管理
│
├── 📂 frontend/              # 前端界面
│   ├── 📂 components/        # React组件
│   │   ├── RealtimeEditor.tsx    # 实时编辑器 (487行)
│   │   ├── useWebSocket.ts       # WebSocket Hook (150行)
│   │   └── types/                # TypeScript类型
│   ├── 📂 app/
│   │   └── editor/page.tsx       # 演示页面 (274行)
│   └── package.json
│
├── 📂 tests/                # 测试用例
│   ├── test_realtime.py         # 单元测试 (600+行)
│   └── test_realtime_integration.py # 集成测试 (1000+行)
│
├── 📂 docs/
│   ├── 📂 design/              # 设计文档
│   ├── 📂 developer/          # 开发文档
│   │   ├── Realtime-Collaboration-System.md
│   │   ├── Realtime-Editor-Guide.md
│   │   └── Phase-6-2-Complete-Summary.md
│   └── 📂 architecture/        # 架构文档
│
├── test_client.js           # WebSocket测试客户端 (237行)
└── README.md
```

## 📊 成功指标

### 用户体验
- 创作效率提升：10倍
- NPC行为真实度：>85%
- 系统响应：<2秒
- 学习曲线：<30分钟

### 技术指标
- 支持节点数：>10,000
- 并发用户：>1,000
- 资产库：>10,000
- 系统可用性：99.9%

### 生态指标
- 活跃创作者：>10,000
- 资产交易额：$1M/月
- 世界数量：>1,000
- 协作项目：>500

## 🤝 贡献指南

欢迎贡献！

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情见 LICENSE 文件。

## 📧 联系

- 项目地址：[GitHub链接]
- 文档：[详细文档链接]

---

**愿景**: 让每个人都能创造自己的宇宙，并与其他宇宙连接，形成无限的想象之网。
