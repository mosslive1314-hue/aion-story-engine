/**
 * 节点可视化编辑器 - 完整编辑器
 */

'use client';

import React, { useState, useCallback } from 'react';
import NodeCanvas from './NodeCanvas';
import type { StoryNode, NodeConnection } from './types/node-editor';
import type { NodeEditorProps } from './types/node-editor';

const NodeEditor: React.FC<NodeEditorProps> = ({
  nodes: initialNodes = [],
  connections: initialConnections = [],
  onNodeChange,
  onNodeDelete,
  onConnectionAdd,
  onConnectionDelete,
  onNodeSelect,
  theme = 'dark',
  className = '',
  style = {}
}) => {
  // 节点状态
  const [nodes, setNodes] = useState<StoryNode[]>(initialNodes);
  const [connections, setConnections] = useState<NodeConnection[]>(initialConnections);

  // 同步外部props变化
  React.useEffect(() => {
    if (initialNodes.length > 0) {
      setNodes(initialNodes);
    }
  }, [initialNodes]);

  React.useEffect(() => {
    if (initialConnections.length > 0) {
      setConnections(initialConnections);
    }
  }, [initialConnections]);

  // 处理节点变更
  const handleNodeChange = useCallback((updatedNode: StoryNode) => {
    setNodes(prev => prev.map(node =>
      node.id === updatedNode.id ? updatedNode : node
    ));
    onNodeChange?.(updatedNode);
  }, [onNodeChange]);

  // 处理节点删除
  const handleNodeDelete = useCallback((nodeId: string) => {
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    // 同时删除相关连接
    setConnections(prev => prev.filter(
      conn => conn.sourceId !== nodeId && conn.targetId !== nodeId
    ));
    onNodeDelete?.(nodeId);
  }, [onNodeDelete]);

  // 处理节点选择
  const handleNodeSelect = useCallback((nodeId: string | null) => {
    onNodeSelect?.(nodeId);
  }, [onNodeSelect]);

  // 容器样式
  const containerStyle: React.CSSProperties = {
    width: '100%',
    height: '100vh',
    backgroundColor: theme === 'dark' ? '#0f0f0f' : '#ffffff',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    ...style
  };

  const headerStyle: React.CSSProperties = {
    padding: '16px 24px',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  return (
    <div className={`node-editor ${className}`} style={containerStyle}>
      {/* 头部 */}
      <div style={headerStyle}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: '20px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🌳 节点可视化编辑器
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#666' }}>
            可视化管理故事节点树
          </p>
        </div>

        <div style={{ fontSize: '14px', color: '#666' }}>
          节点: {nodes.length} | 连接: {connections.length}
        </div>
      </div>

      {/* 画布 */}
      <NodeCanvas
        nodes={nodes}
        connections={connections}
        onNodeChange={handleNodeChange}
        onNodeDelete={handleNodeDelete}
        onNodeSelect={handleNodeSelect}
        theme={theme}
        style={{ flex: 1 }}
      />
    </div>
  );
};

export default NodeEditor;
