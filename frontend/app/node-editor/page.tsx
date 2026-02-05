/**
 * 节点可视化编辑器演示页面
 */

'use client';

import React, { useState } from 'react';
import NodeEditor from '../../../components/NodeEditor';
import type { StoryNode, NodeConnection } from '../../../components/types/node-editor';

export default function NodeEditorPage() {
  // 示例节点数据
  const [nodes, setNodes] = useState<StoryNode[]>([
    {
      id: 'root-1',
      type: 'root',
      title: '我的故事宇宙',
      description: '故事的根节点',
      position: { x: 400, y: 50 },
      status: 'completed',
      children: ['story-1', 'story-2'],
      createdAt: new Date('2026-01-01'),
      updatedAt: new Date('2026-01-01')
    },
    {
      id: 'story-1',
      type: 'story',
      title: '第一章：启程',
      description: '冒险的开始',
      parentId: 'root-1',
      position: { x: 200, y: 200 },
      status: 'completed',
      children: ['chapter-1', 'chapter-2'],
      createdAt: new Date('2026-01-01'),
      updatedAt: new Date('2026-01-02')
    },
    {
      id: 'story-2',
      type: 'story',
      title: '第二章：探索',
      description: '未知的领域',
      parentId: 'root-1',
      position: { x: 600, y: 200 },
      status: 'in-progress',
      children: ['chapter-3'],
      createdAt: new Date('2026-01-03'),
      updatedAt: new Date('2026-01-03')
    },
    {
      id: 'chapter-1',
      type: 'chapter',
      title: '出发前的准备',
      content: '主角收拾行李，与朋友道别...',
      parentId: 'story-1',
      position: { x: 100, y: 350 },
      status: 'completed',
      children: ['scene-1', 'scene-2'],
      createdAt: new Date('2026-01-01'),
      updatedAt: new Date('2026-01-02')
    },
    {
      id: 'chapter-2',
      type: 'chapter',
      title: '初次冒险',
      content: '主角遇到了第一个挑战...',
      parentId: 'story-1',
      position: { x: 300, y: 350 },
      status: 'completed',
      children: ['scene-3'],
      createdAt: new Date('2026-01-02'),
      updatedAt: new Date('2026-01-03')
    },
    {
      id: 'chapter-3',
      type: 'chapter',
      title: '神秘森林',
      content: '进入了一片神秘的森林...',
      parentId: 'story-2',
      position: { x: 600, y: 350 },
      status: 'draft',
      children: [],
      createdAt: new Date('2026-01-04'),
      updatedAt: new Date('2026-01-04')
    },
    {
      id: 'scene-1',
      type: 'scene',
      title: '卧室告别',
      content: '清晨的阳光透过窗户...',
      parentId: 'chapter-1',
      position: { x: 50, y: 500 },
      status: 'completed',
      children: [],
      createdAt: new Date('2026-01-01'),
      updatedAt: new Date('2026-01-01')
    },
    {
      id: 'scene-2',
      type: 'scene',
      title: '火车站',
      content: '喧闹的人群，告别的站台...',
      parentId: 'chapter-1',
      position: { x: 150, y: 500 },
      status: 'completed',
      children: ['char-1'],
      createdAt: new Date('2026-01-01'),
      updatedAt: new Date('2026-01-02')
    },
    {
      id: 'scene-3',
      type: 'scene',
      title: '森林入口',
      content: '巨大的树木，阳光透过树叶...',
      parentId: 'chapter-2',
      position: { x: 300, y: 500 },
      status: 'completed',
      children: ['char-2', 'loc-1'],
      createdAt: new Date('2026-01-02'),
      updatedAt: new Date('2026-01-03')
    },
    {
      id: 'char-1',
      type: 'character',
      title: '艾莉斯',
      description: '主角的挚友',
      position: { x: 150, y: 650 },
      status: 'completed',
      children: [],
      metadata: { role: 'companion', age: 18 },
      createdAt: new Date('2026-01-01'),
      updatedAt: new Date('2026-01-01')
    },
    {
      id: 'char-2',
      type: 'character',
      title: '神秘老人',
      description: '森林中的智者',
      position: { x: 300, y: 650 },
      status: 'in-progress',
      children: [],
      metadata: { role: 'mentor', mysterious: true },
      createdAt: new Date('2026-01-03'),
      updatedAt: new Date('2026-01-03')
    },
    {
      id: 'loc-1',
      type: 'location',
      title: '古老森林',
      description: '充满魔力的原始森林',
      position: { x: 450, y: 500 },
      status: 'draft',
      children: ['item-1'],
      createdAt: new Date('2026-01-03'),
      updatedAt: new Date('2026-01-03')
    },
    {
      id: 'item-1',
      type: 'item',
      title: '魔法地图',
      description: '显示未知区域的地图',
      position: { x: 450, y: 650 },
      status: 'draft',
      children: [],
      metadata: { rarity: 'rare', magical: true },
      createdAt: new Date('2026-01-03'),
      updatedAt: new Date('2026-01-03')
    }
  ]);

  // 示例连接数据
  const [connections, setConnections] = useState<NodeConnection[]>([
    {
      id: 'conn-1',
      sourceId: 'root-1',
      targetId: 'story-1',
      type: 'solid',
      color: '#667eea'
    },
    {
      id: 'conn-2',
      sourceId: 'root-1',
      targetId: 'story-2',
      type: 'solid',
      color: '#667eea'
    },
    {
      id: 'conn-3',
      sourceId: 'story-1',
      targetId: 'chapter-1',
      type: 'solid',
      color: '#764ba2'
    },
    {
      id: 'conn-4',
      sourceId: 'story-1',
      targetId: 'chapter-2',
      type: 'solid',
      color: '#764ba2'
    },
    {
      id: 'conn-5',
      sourceId: 'story-2',
      targetId: 'chapter-3',
      type: 'dashed',
      color: '#9ca3af',
      label: '待定'
    },
    {
      id: 'conn-6',
      sourceId: 'chapter-1',
      targetId: 'scene-1',
      type: 'solid',
      color: '#4facfe'
    },
    {
      id: 'conn-7',
      sourceId: 'chapter-1',
      targetId: 'scene-2',
      type: 'solid',
      color: '#4facfe'
    },
    {
      id: 'conn-8',
      sourceId: 'chapter-2',
      targetId: 'scene-3',
      type: 'solid',
      color: '#4facfe'
    },
    {
      id: 'conn-9',
      sourceId: 'scene-2',
      targetId: 'char-1',
      type: 'dotted',
      color: '#43e97b'
    },
    {
      id: 'conn-10',
      sourceId: 'scene-3',
      targetId: 'char-2',
      type: 'dotted',
      color: '#43e97b'
    },
    {
      id: 'conn-11',
      sourceId: 'scene-3',
      targetId: 'loc-1',
      type: 'solid',
      color: '#fa709a'
    },
    {
      id: 'conn-12',
      sourceId: 'loc-1',
      targetId: 'item-1',
      type: 'dotted',
      color: '#fee140'
    }
  ]);

  // 处理节点变更
  const handleNodeChange = (updatedNode: StoryNode) => {
    setNodes(prev => prev.map(node =>
      node.id === updatedNode.id ? updatedNode : node
    ));
    console.log('Node updated:', updatedNode);
  };

  // 处理节点删除
  const handleNodeDelete = (nodeId: string) => {
    console.log('Node deleted:', nodeId);
  };

  // 处理节点选择
  const handleNodeSelect = (nodeId: string | null) => {
    console.log('Node selected:', nodeId);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      {/* 页面头部 */}
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
            🌳 节点可视化编辑器演示
          </h1>
          <p style={{ margin: '8px 0 0 0', color: '#666' }}>
            可视化管理和编辑故事节点树
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{
            padding: '8px 16px',
            background: '#f3f4f6',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#666'
          }}>
            💡 提示: 双击节点打开属性面板
          </div>
          <div style={{
            padding: '8px 16px',
            background: '#f3f4f6',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#666'
          }}>
            🔍 Ctrl+滚轮: 缩放画布
          </div>
          <div style={{
            padding: '8px 16px',
            background: '#f3f4f6',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#666'
          }}>
            ✋ 拖拽: 移动节点
          </div>
        </div>
      </div>

      {/* 编辑器 */}
      <div style={{
        flex: 1,
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        overflow: 'hidden',
        height: 'calc(100vh - 180px)'
      }}>
        <NodeEditor
          nodes={nodes}
          connections={connections}
          onNodeChange={handleNodeChange}
          onNodeDelete={handleNodeDelete}
          onNodeSelect={handleNodeSelect}
          theme="dark"
          style={{ height: '100%' }}
        />
      </div>

      {/* 页脚 */}
      <div style={{
        marginTop: '20px',
        background: 'white',
        borderRadius: '8px',
        padding: '16px',
        textAlign: 'center',
        fontSize: '12px',
        color: '#999',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        AION Story Engine - Phase 6.3 节点可视化编辑器 | © 2026
      </div>
    </div>
  );
}
