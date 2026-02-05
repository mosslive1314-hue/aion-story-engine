# 实时协作编辑器 (Real-time Collaborative Editor)

## 概述

实时协作编辑器是 AION Story Engine 的核心组件之一，提供多用户实时协作编辑体验。该编辑器集成了 WebSocket 通信、实时同步引擎和冲突解决机制。

## 功能特性

### ✨ 核心功能
- **实时同步编辑** - 多用户可以同时编辑同一个文档
- **光标位置显示** - 实时显示其他用户的光标位置
- **用户在线状态** - 显示当前在线的用户列表
- **冲突自动解决** - 基于操作变换(OT)的冲突解决机制
- **视觉反馈** - 优雅的 UI 设计和动画效果

### 🎨 用户界面
- 现代化的渐变设计
- 响应式布局
- 用户头像和颜色编码
- 连接状态指示器
- 实时统计信息

### 🔧 技术特性
- 基于 WebSocket 的实时通信
- 与同步引擎深度集成
- 支持分支和快照
- 版本向量追踪
- 操作变换算法

## 组件架构

### 1. RealtimeEditor 主组件
位置: `frontend/components/RealtimeEditor.tsx`

```typescript
interface RealtimeEditorProps {
  documentId: string;      // 文档 ID
  userId: string;          // 用户 ID
  username: string;         // 用户名
  initialContent?: string;  // 初始内容
  websocketUrl?: string;    // WebSocket 服务器地址
  onContentChange?: (content: string) => void; // 内容变更回调
}
```

### 2. useWebSocket Hook
位置: `frontend/components/useWebSocket.ts`

管理 WebSocket 连接和消息传递。

```typescript
const {
  connected,              // 连接状态
  connectionStatus,      // 连接状态 ('connecting' | 'connected' | 'disconnected')
  remoteUsers,           // 远程用户 Map
  sendCursorPosition,    // 发送光标位置
  sendChange,            // 发送变更
  sendSelection          // 发送选择范围
} = useWebSocket({
  documentId,
  userId,
  username,
  websocketUrl,
  onCursorChange: (data) => { /* 处理光标变更 */ },
  onContentChange: (data) => { /* 处理内容变更 */ }
});
```

### 3. 类型定义
位置: `frontend/components/types/realtime.ts`

定义了所有 WebSocket 消息和实体的类型。

## 使用方法

### 基本使用

```typescript
import RealtimeEditor from './components/RealtimeEditor';

function MyComponent() {
  return (
    <RealtimeEditor
      documentId="my-document"
      userId="user-123"
      username="张三"
      initialContent="初始内容..."
      websocketUrl="ws://localhost:8765"
      onContentChange={(content) => {
        console.log('内容变更:', content);
      }}
    />
  );
}
```

### WebSocket 消息格式

#### 加入房间
```json
{
  "type": "join",
  "room_id": "document-id",
  "user_id": "user-123",
  "data": {
    "user": {
      "user_id": "user-123",
      "username": "张三",
      "color": "#FF6B6B"
    }
  }
}
```

#### 光标位置
```json
{
  "type": "cursor",
  "room_id": "document-id",
  "user_id": "user-123",
  "data": {
    "cursor_position": 42,
    "username": "张三",
    "color": "#FF6B6B"
  }
}
```

#### 内容变更
```json
{
  "type": "change",
  "room_id": "document-id",
  "user_id": "user-123",
  "data": {
    "operation": {
      "type": "insert",
      "position": 42,
      "content": "新文本",
      "user_id": "user-123"
    }
  }
}
```

## WebSocket 服务器集成

### 启动 WebSocket 服务器

```bash
python -m aion_engine.realtime.websocket
```

服务器将在 `ws://localhost:8765` 监听连接。

### 消息类型

| 类型 | 描述 |
|------|------|
| `join` | 用户加入房间 |
| `leave` | 用户离开房间 |
| `cursor` | 光标位置更新 |
| `selection` | 选择范围更新 |
| `change` | 内容变更 |
| `sync` | 同步请求 |
| `ping` | 心跳检测 |
| `presence` | 在线状态更新 |

## 高级功能

### 1. 操作变换 (OT)

编辑器内置了先进的操作变换算法，能够智能处理并发编辑冲突：

- **插入-插入冲突** - 根据位置和时间戳排序
- **删除-删除冲突** - 合并重叠范围
- **插入-删除冲突** - 调整位置偏移

### 2. 版本向量

用于分布式一致性：

```typescript
const vector = engine.get_version_vector('document-id');
console.log(vector.get_version('user-123')); // 获取用户版本
```

### 3. 分支管理

支持文档分支：

```typescript
engine.create_branch('doc1', 'feature-branch');
engine.merge_branch('doc1', 'feature-branch', 'main');
```

### 4. 快照系统

创建和恢复快照：

```typescript
engine.create_snapshot('doc1', 'snapshot-1');
engine.restore_snapshot('doc1', 'snapshot-1');
```

### 5. 撤销/重做

```typescript
engine.undo('doc1', 'user123');  // 撤销
engine.redo('doc1', 'user123');   // 重做
```

## 演示页面

访问 `/editor` 路径查看交互式演示：

```
http://localhost:3000/editor
```

演示页面允许：
- 输入用户名和文档 ID
- 实时协作编辑
- 查看在线用户
- 观察光标位置
- 体验冲突解决

## 样式定制

编辑器使用 CSS-in-JS 样式，可以通过修改 `style jsx` 部分来自定义外观：

```typescript
// 修改主题颜色
background: linear-gradient(135deg, #your-color1 0%, #your-color2 100%)

// 自定义编辑器字体
font-family: 'Your-Font', monospace

// 调整光标样式
.remote-cursor {
  width: 3px;  // 更粗的光标
  background: 'your-color';
}
```

## 性能优化

1. **节流光标更新** - 避免过于频繁的光标位置发送
2. **批量操作** - 使用 `apply_batch_operations` 合并多个操作
3. **虚拟滚动** - 对大文档使用虚拟滚动
4. **操作历史限制** - 限制撤销栈大小（默认 100）

## 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 开发指南

### 添加新消息类型

1. 在 `types/realtime.ts` 中添加枚举值
2. 在 `useWebSocket.ts` 中添加处理逻辑
3. 在编辑器组件中实现 UI 反馈

### 扩展冲突解决

1. 在 `AdvancedConflictResolver` 类中添加新的变换算法
2. 在 `RealtimeSyncEngine` 中应用变换
3. 添加相应的测试用例

## 故障排除

### WebSocket 连接失败
- 检查服务器是否启动：`python -m aion_engine.realtime.websocket`
- 验证 WebSocket URL 是否正确
- 查看浏览器控制台错误信息

### 协作不同步
- 检查操作变换逻辑
- 验证版本向量更新
- 查看冲突检测代码

### 性能问题
- 限制撤销栈大小
- 优化光标更新频率
- 使用批量操作

## 相关资源

- [WebSocket API 文档](../api/WebSocket.md)
- [同步引擎文档](../engine/Sync.md)
- [冲突解决算法](../algorithms/ConflictResolution.md)

## 贡献

欢迎提交 Issue 和 Pull Request 来改进实时协作编辑器！

## 许可证

MIT License © 2026 AION Story Engine
