/**
 * 节点画布组件
 * 显示和管理节点树
 */

'use client';

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import NodeItem from './NodeItem';
import NodeConnections from './NodeConnections';
import NodeProperties from './NodeProperties';
import type { StoryNode, NodeConnection, ViewportState, SelectionState, CanvasEvent } from '../types/node-editor';

interface NodeCanvasProps {
  nodes: StoryNode[];
  connections?: NodeConnection[];
  onNodeChange?: (node: StoryNode) => void;
  onNodeDelete?: (nodeId: string) => void;
  onNodeSelect?: (nodeId: string | null) => void;
  theme?: 'light' | 'dark';
  className?: string;
  style?: React.CSSProperties;
}

const NodeCanvas: React.FC<NodeCanvasProps> = ({
  nodes,
  connections = [],
  onNodeChange,
  onNodeDelete,
  onNodeSelect,
  theme = 'dark',
  className = '',
  style = {}
}) => {
  // 视口状态
  const [viewport, setViewport] = useState<ViewportState>({
    scale: 1,
    offset: { x: 0, y: 0 }
  });

  // 选择状态
  const [selection, setSelection] = useState<SelectionState>({
    selectedNodes: new Set<string>(),
    selectedConnections: new Set<string>(),
    isDragging: false,
    dragStart: { x: 0, y: 0 }
  });

  // 属性面板状态
  const [propertyPanel, setPropertyPanel] = useState({
    node: null as StoryNode | null,
    visible: false,
    position: { x: 0, y: 0 }
  });

  const canvasRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });

  // 缩放处理
  const handleZoom = useCallback((delta: number, centerX: number, centerY: number) => {
    setViewport(prev => {
      const newScale = Math.min(Math.max(prev.scale * delta, 0.1), 5);

      return {
        ...prev,
        scale: newScale,
        // 调整偏移以保持缩放中心点不变
        offset: {
          x: centerX - (centerX - prev.offset.x) * (newScale / prev.scale),
          y: centerY - (centerY - prev.offset.y) * (newScale / prev.scale)
        }
      };
    });
  }, []);

  // 平移处理
  const handlePan = useCallback((deltaX: number, deltaY: number) => {
    setViewport(prev => ({
      ...prev,
      offset: {
        x: prev.offset.x + deltaX,
        y: prev.offset.y + deltaY
      }
    }));
  }, []);

  // 处理节点点击
  const handleNodeClick = useCallback((node: StoryNode) => {
    setSelection(prev => ({
      ...prev,
      selectedNodes: new Set([node.id])
    }));
    onNodeSelect?.(node.id);
  }, [onNodeSelect]);

  // 处理节点双击（打开属性面板）
  const handleNodeDoubleClick = useCallback((node: StoryNode) => {
    setPropertyPanel({
      node,
      visible: true,
      position: { x: node.position.x + 200, y: node.position.y }
    });
  }, []);

  // 处理画布点击（取消选择）
  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setSelection(prev => ({
        ...prev,
        selectedNodes: new Set(),
        selectedConnections: new Set()
      }));
      onNodeSelect?.(null);
    }
  }, [onNodeSelect]);

  // 处理鼠标滚轮（缩放）
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();

    if (e.ctrlKey || e.metaKey) {
      // 缩放
      const rect = canvasRef.current?.getBoundingClientRect();
      if (rect) {
        const centerX = e.clientX - rect.left;
        const centerY = e.clientY - rect.top;
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        handleZoom(delta, centerX, centerY);
      }
    } else {
      // 平移
      handlePan(e.deltaX, e.deltaY);
    }
  }, [handleZoom, handlePan]);

  // 处理保存
  const handleSave = useCallback((updatedNode: StoryNode) => {
    onNodeChange?.(updatedNode);
  }, [onNodeChange]);

  // 处理删除
  const handleDelete = useCallback((nodeId: string) => {
    onNodeDelete?.(nodeId);
    setPropertyPanel(prev => ({ ...prev, visible: false }));
  }, [onNodeDelete]);

  // 转换坐标（屏幕坐标 → 画布坐标）
  const screenToCanvas = useCallback((screenX: number, screenY: number) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };

    return {
      x: (screenX - rect.left - viewport.offset.x) / viewport.scale,
      y: (screenY - rect.top - viewport.offset.y) / viewport.scale
    };
  }, [viewport]);

  // 画布样式
  const canvasStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100%',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    backgroundImage: theme === 'dark'
      ? 'radial-gradient(circle at 1px 1px, #3f3f46 1px, transparent 0)'
      : 'radial-gradient(circle at 1px 1px, #e4e4e7 1px, transparent 0)',
    backgroundSize: '20px 20px',
    overflow: 'hidden',
    cursor: selection.isDragging ? 'grabbing' : 'grab',
    userSelect: 'none',
    ...style
  };

  // 内容容器样式
  const contentStyle: React.CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    transform: `translate(${viewport.offset.x}px, ${viewport.offset.y}px) scale(${viewport.scale})`,
    transformOrigin: '0 0',
    width: '100%',
    height: '100%'
  };

  // 工具栏样式
  const toolbarStyle: React.CSSProperties = {
    position: 'absolute',
    top: '20px',
    left: '20px',
    display: 'flex',
    gap: '8px',
    zIndex: 100
  };

  const toolbarButtonStyle: React.CSSProperties = {
    padding: '8px 16px',
    background: theme === 'dark' ? '#2d2d2d' : '#ffffff',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '6px',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
    fontSize: '14px',
    cursor: 'pointer',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  // 节点列表
  const nodesList = useMemo(() => {
    return nodes.map(node => ({
      ...node,
      position: node.position || { x: Math.random() * 800, y: Math.random() * 600 },
      size: node.size || { width: 150, height: 80 },
      status: node.status || 'draft',
      createdAt: node.createdAt instanceof Date ? node.createdAt : new Date(node.createdAt),
      updatedAt: node.updatedAt instanceof Date ? node.updatedAt : new Date(node.updatedAt)
    }));
  }, [nodes]);

  return (
    <div
      className={`node-canvas ${className}`}
      style={canvasStyle}
      ref={canvasRef}
      onClick={handleCanvasClick}
      onWheel={handleWheel}
    >
      {/* 工具栏 */}
      <div style={toolbarStyle}>
        <button
          style={toolbarButtonStyle}
          onClick={() => handleZoom(1.2, window.innerWidth / 2, window.innerHeight / 2)}
          title="放大"
        >
          🔍+
        </button>
        <button
          style={toolbarButtonStyle}
          onClick={() => handleZoom(0.8, window.innerWidth / 2, window.innerHeight / 2)}
          title="缩小"
        >
          🔍-
        </button>
        <button
          style={toolbarButtonStyle}
          onClick={() => setViewport({ scale: 1, offset: { x: 0, y: 0 } })}
          title="重置视图"
        >
          🎯
        </button>
        <div style={{
          padding: '8px 16px',
          background: theme === 'dark' ? '#2d2d2d' : '#ffffff',
          border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
          borderRadius: '6px',
          fontSize: '12px',
          color: theme === 'dark' ? '#e4e4e7' : '#18181b'
        }}>
          缩放: {Math.round(viewport.scale * 100)}%
        </div>
      </div>

      {/* 内容区 */}
      <div style={contentStyle}>
        {/* 连接线 */}
        <NodeConnections
          connections={connections}
          nodes={nodesList}
          theme={theme}
        />

        {/* 节点 */}
        {nodesList.map((node) => (
          <NodeItem
            key={node.id}
            node={node}
            selected={selection.selectedNodes.has(node.id)}
            onClick={handleNodeClick}
            onDoubleClick={handleNodeDoubleClick}
            theme={theme}
          />
        ))}
      </div>

      {/* 属性面板 */}
      <NodeProperties
        node={propertyPanel.node}
        visible={propertyPanel.visible}
        onClose={() => setPropertyPanel(prev => ({ ...prev, visible: false }))}
        onSave={handleSave}
        onDelete={handleDelete}
        theme={theme}
      />
    </div>
  );
};

export default NodeCanvas;
