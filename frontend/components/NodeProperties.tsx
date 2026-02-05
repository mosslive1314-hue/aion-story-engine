/**
 * 节点属性面板组件
 * 编辑节点的详细属性
 */

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import type { StoryNode, NodeType, NodeStatus } from '../types/node-editor';

interface NodePropertiesProps {
  node: StoryNode | null;
  visible: boolean;
  onClose?: () => void;
  onSave?: (node: StoryNode) => void;
  onDelete?: (nodeId: string) => void;
  theme?: 'light' | 'dark';
}

const NodeProperties: React.FC<NodePropertiesProps> = ({
  node,
  visible,
  onClose,
  onSave,
  onDelete,
  theme = 'dark'
}) => {
  // 编辑状态
  const [editingNode, setEditingNode] = useState<StoryNode | null>(node);

  // 当node变化时更新编辑状态
  React.useEffect(() => {
    setEditingNode(node);
  }, [node]);

  // 处理字段变更
  const handleChange = useCallback((field: keyof StoryNode, value: any) => {
    if (!editingNode) return;

    setEditingNode({
      ...editingNode,
      [field]: value,
      updatedAt: new Date()
    });
  }, [editingNode]);

  // 处理保存
  const handleSave = useCallback(() => {
    if (editingNode) {
      onSave?.(editingNode);
    }
  }, [editingNode, onSave]);

  // 处理删除
  const handleDelete = useCallback(() => {
    if (editingNode) {
      onDelete?.(editingNode.id);
      onClose?.();
    }
  }, [editingNode, onDelete, onClose]);

  // 面板样式
  const panelStyle: React.CSSProperties = {
    position: 'fixed',
    right: visible ? '0' : '-400px',
    top: '0',
    width: '400px',
    height: '100vh',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
    borderLeft: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    boxShadow: '-4px 0 12px rgba(0,0,0,0.1)',
    padding: '20px',
    overflow: 'auto',
    transition: 'right 0.3s ease',
    zIndex: 1000,
    display: 'flex',
    flexDirection: 'column'
  };

  const fieldStyle: React.CSSProperties = {
    marginBottom: '20px'
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '600',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b'
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px 12px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
    outline: 'none',
    transition: 'border-color 0.2s'
  };

  const textareaStyle: React.CSSProperties = {
    ...inputStyle,
    minHeight: '100px',
    resize: 'vertical',
    fontFamily: 'monospace'
  };

  if (!editingNode) {
    return null;
  }

  return (
    <div style={panelStyle}>
      {/* 头部 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        paddingBottom: '16px',
        borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`
      }}>
        <h2 style={{
          margin: 0,
          fontSize: '20px',
          fontWeight: 'bold',
          color: theme === 'dark' ? '#e4e4e7' : '#18181b'
        }}>
          节点属性
        </h2>
        <button
          onClick={onClose}
          style={{
            padding: '6px 12px',
            background: 'transparent',
            border: 'none',
            color: theme === 'dark' ? '#a1a1aa' : '#71717a',
            cursor: 'pointer',
            fontSize: '20px'
          }}
        >
          ✕
        </button>
      </div>

      {/* 节点ID（只读） */}
      <div style={fieldStyle}>
        <label style={labelStyle}>节点ID</label>
        <input
          type="text"
          value={editingNode.id}
          disabled
          style={{
            ...inputStyle,
            opacity: 0.5,
            cursor: 'not-allowed'
          }}
        />
      </div>

      {/* 节点标题 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>标题</label>
        <input
          type="text"
          value={editingNode.title}
          onChange={(e) => handleChange('title', e.target.value)}
          style={inputStyle}
          placeholder="输入节点标题"
        />
      </div>

      {/* 节点类型 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>类型</label>
        <select
          value={editingNode.type}
          onChange={(e) => handleChange('type', e.target.value as NodeType)}
          style={inputStyle}
        >
          <option value="root">根节点 🌟</option>
          <option value="story">故事 📖</option>
          <option value="chapter">章节 📑</option>
          <option value="scene">场景 🎬</option>
          <option value="character">角色 👤</option>
          <option value="location">地点 🏠</option>
          <option value="item">物品 🎁</option>
          <option value="choice">选择 🔀</option>
        </select>
      </div>

      {/* 节点状态 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>状态</label>
        <select
          value={editingNode.status}
          onChange={(e) => handleChange('status', e.target.value as NodeStatus)}
          style={inputStyle}
        >
          <option value="draft">草稿 📝</option>
          <option value="in-progress">进行中 ⏳</option>
          <option value="completed">已完成 ✅</option>
          <option value="archived">已归档 📦</option>
        </select>
      </div>

      {/* 描述 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>描述</label>
        <textarea
          value={editingNode.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          style={textareaStyle}
          placeholder="输入节点描述"
          rows={3}
        />
      </div>

      {/* 内容 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>内容</label>
        <textarea
          value={editingNode.content || ''}
          onChange={(e) => handleChange('content', e.target.value)}
          style={textareaStyle}
          placeholder="输入节点内容"
          rows={6}
        />
      </div>

      {/* 位置信息 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>位置</label>
        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ ...labelStyle, fontSize: '12px' }}>X</label>
            <input
              type="number"
              value={editingNode.position.x}
              onChange={(e) => handleChange('position', {
                ...editingNode.position,
                x: parseFloat(e.target.value)
              })}
              style={inputStyle}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ ...labelStyle, fontSize: '12px' }}>Y</label>
            <input
              type="number"
              value={editingNode.position.y}
              onChange={(e) => handleChange('position', {
                ...editingNode.position,
                y: parseFloat(e.target.value)
              })}
              style={inputStyle}
            />
          </div>
        </div>
      </div>

      {/* 尺寸 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>尺寸</label>
        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ ...labelStyle, fontSize: '12px' }}>宽度</label>
            <input
              type="number"
              value={editingNode.size?.width || 150}
              onChange={(e) => handleChange('size', {
                ...editingNode.size,
                width: parseFloat(e.target.value)
              })}
              style={inputStyle}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ ...labelStyle, fontSize: '12px' }}>高度</label>
            <input
              type="number"
              value={editingNode.size?.height || 80}
              onChange={(e) => handleChange('size', {
                ...editingNode.size,
                height: parseFloat(e.target.value)
              })}
              style={inputStyle}
            />
          </div>
        </div>
      </div>

      {/* 元数据 */}
      <div style={fieldStyle}>
        <label style={labelStyle}>元数据 (JSON)</label>
        <textarea
          value={JSON.stringify(editingNode.metadata || {}, null, 2)}
          onChange={(e) => {
            try {
              const metadata = JSON.parse(e.target.value);
              handleChange('metadata', metadata);
            } catch {
              // 忽略无效JSON
            }
          }}
          style={textareaStyle}
          rows={4}
        />
      </div>

      {/* 统计信息 */}
      <div style={{
        marginTop: '20px',
        padding: '12px',
        backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f4f4f4',
        borderRadius: '6px',
        fontSize: '12px',
        color: theme === 'dark' ? '#a1a1aa' : '#71717a'
      }}>
        <div>子节点数: {editingNode.children.length}</div>
        <div>创建时间: {editingNode.createdAt.toLocaleString()}</div>
        <div>更新时间: {editingNode.updatedAt.toLocaleString()}</div>
      </div>

      {/* 操作按钮 */}
      <div style={{
        marginTop: 'auto',
        paddingTop: '20px',
        borderTop: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
        display: 'flex',
        gap: '12px'
      }}>
        <button
          onClick={handleDelete}
          style={{
            flex: 1,
            padding: '10px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          删除节点
        </button>
        <button
          onClick={handleSave}
          style={{
            flex: 1,
            padding: '10px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          保存更改
        </button>
      </div>
    </div>
  );
};

export default NodeProperties;
