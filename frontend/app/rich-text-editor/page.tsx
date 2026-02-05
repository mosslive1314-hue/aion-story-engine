/**
 * 富文本编辑器演示页面
 */

'use client';

import React, { useState } from 'react';
import RichTextEditor from '../../../components/RichTextEditor';

export default function RichTextEditorPage() {
  const [content, setContent] = useState(`# 欢迎使用 AION 富文本编辑器 🌟

这是一个支持 **Markdown** 的富文本编辑器，具有实时预览功能。

## ✨ 主要功能

### 1. 实时预览
- **编辑模式**: 专注于写作
- **预览模式**: 查看渲染效果
- **分屏模式**: 同时编辑和预览

### 2. 格式化支持
- **标题**: \`# H1\`, \`## H2\`, \`### H3\`
- **粗体**: \`**文本**\`
- **斜体**: \`*文本*\`
- **代码**: \`\`代码\`\`或代码块
- **引用**: \`> 引用文本\`
- **列表**: 无序列表和有序列表
- **任务列表**: \`- [ ] 待办\`
- **链接**: \`[文本](url)\`
- **图片**: \`![alt](url)\`

### 3. 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl/Cmd + S | 保存 |
| Ctrl/Cmd + B | 粗体 |
| Ctrl/Cmd + I | 斜体 |
| Ctrl/Cmd + K | 链接 |
| Ctrl/Cmd + \\\` | 代码 |
| Tab | 缩进 |
| Esc | 退出全屏 |

## 代码示例

\`\`\`javascript
// JavaScript 代码高亮
function greet(name) {
  console.log(\`Hello, \${name}!\`);
  return \`Welcome to AION Story Engine!\`;
}

greet('Creator');
\`\`\`

## 引用示例

> "写作是一种探索，通过文字发现未知的自己。"
> —— AION Story Engine

## 列表示例

### 无序列表
- 📝 创建节点
- 🌌 探索宇宙
- 🎭 塑造角色
- 📖 编写故事

### 有序列表
1. 构思情节
2. 创建角色
3. 设计世界
4. 编写场景

### 任务列表
- [x] 完成Phase 6.2
- [x] 构建实时协作系统
- [ ] 完成Phase 6.3
- [ ] 添加富文本编辑
- [ ] 添加节点可视化

## 链接和图片

[访问 AION Story Engine](https://github.com/aion/story-engine)

## 开始创作吧！ ✍️

在左侧编辑，右侧实时预览。使用工具栏快速插入格式化元素。
`);

  const [wordCount, setWordCount] = useState(0);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const handleSave = (newContent: string) => {
    setLastSaved(new Date());
    // 这里可以添加保存逻辑，例如调用API
    console.log('Saving content:', newContent.substring(0, 100) + '...');
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '20px 24px',
        marginBottom: '20px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: '28px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🌟 AION 富文本编辑器
          </h1>
          <p style={{ margin: '8px 0 0 0', color: '#666' }}>
            支持 Markdown 实时预览和语法高亮
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {lastSaved && (
            <div style={{ fontSize: '14px', color: '#71717a' }}>
              上次保存: {lastSaved.toLocaleTimeString()}
            </div>
          )}
          <div style={{
            padding: '8px 16px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            字数: {wordCount}
          </div>
        </div>
      </div>

      {/* Editor */}
      <div style={{ flex: 1 }}>
        <RichTextEditor
          initialValue={content}
          onChange={setContent}
          onSave={handleSave}
          onWordCountChange={setWordCount}
          theme="dark"
          style={{ height: 'calc(100vh - 180px)' }}
        />
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '20px',
        background: 'white',
        borderRadius: '8px',
        padding: '16px',
        textAlign: 'center',
        fontSize: '14px',
        color: '#999',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        AION Story Engine - Phase 6.3 富文本编辑器 | 支持 Markdown 实时预览 | © 2026
      </div>
    </div>
  );
}
