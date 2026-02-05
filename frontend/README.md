# AION Story Engine - Frontend

基于 Next.js 和 React 的 Web 前端界面，为 AION Story Engine 提供直观的创作和管理体验。

## 🚀 特性

- **故事编辑器** - 可视化节点树编辑器，支持分支和合并
- **多人协作** - 实时协作功能，团队共同创作
- **资产市场** - 浏览和分享创作资产
- **用户仪表板** - 管理所有项目和协作
- **响应式设计** - 适配各种设备尺寸

## 🛠️ 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: React Query
- **UI 组件**: Lucide React Icons
- **图表**: D3.js (用于节点可视化)
- **测试**: Jest

## 📦 安装

```bash
cd frontend
npm install
```

## 🔧 开发

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm run start

# 代码检查
npm run lint

# 类型检查
npm run type-check

# 运行测试
npm test
```

## 🎨 设计系统

### 配色方案

- **Cosmic Blue**: #0B1426 (主背景)
- **Nebula Purple**: #1E1B3E (卡片背景)
- **Star White**: #E8E9F3 (主文字)
- **Plasma Pink**: #FF00AA (强调色)
- **Quantum Green**: #00FF88 (成功/积极)

### 组件

#### 按钮

```jsx
<button className="btn-primary">主要按钮</button>
<button className="btn-secondary">次要按钮</button>
```

#### 卡片

```jsx
<div className="card">
  <h3>卡片标题</h3>
  <p>卡片内容</p>
</div>
```

#### 输入框

```jsx
<input className="input-field" placeholder="输入文本..." />
```

## 📁 项目结构

```
frontend/
├── app/                    # Next.js App Router 页面
│   ├── dashboard/          # 用户仪表板
│   ├── stories/           # 故事管理
│   │   └── [id]/          # 故事编辑器
│   ├── marketplace/       # 资产市场
│   ├── globals.css        # 全局样式
│   ├── layout.tsx         # 根布局
│   └── page.tsx           # 首页
├── components/            # 可复用组件
│   └── Navigation.tsx     # 导航栏
├── lib/                   # 工具库
│   ├── api.ts             # API 客户端
│   └── utils.ts           # 工具函数
├── tests/                 # 测试文件
├── public/                # 静态资源
└── package.json           # 依赖配置
```

## 🔌 API 集成

前端通过 `/lib/api.ts` 中的客户端与后端 API 通信：

```typescript
// 获取故事列表
const sessions = await api.getSessions();

// 创建新故事
const session = await api.createSession('My Story');

// 获取市场资产
const assets = await api.getMarketplaceAssets();
```

## 🧪 测试

运行测试：

```bash
npm test
```

运行测试并生成覆盖率报告：

```bash
npm test -- --coverage
```

## 🌐 部署

### Vercel 部署

1. 将代码推送到 GitHub
2. 在 [Vercel](https://vercel.com) 导入项目
3. 配置环境变量：
   - `NEXT_PUBLIC_API_URL`: 后端 API 地址

### Docker 部署

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📝 开发指南

### 添加新页面

1. 在 `app/` 目录下创建文件夹
2. 添加 `page.tsx` 文件
3. 导出默认组件

### 添加新组件

1. 在 `components/` 目录创建组件文件
2. 使用 `'use client'` 指令标记客户端组件
3. 导出组件

### 连接 API

1. 在 `lib/api.ts` 中添加 API 函数
2. 使用 TypeScript 定义类型
3. 在页面中导入并使用

## 🤝 贡献

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

MIT License
