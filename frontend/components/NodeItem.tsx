/**
 * 节点组件
 * 显示单个故事节点
 */

'use client';

import React, { useMemo } from 'react';
import type { StoryNode, NodeType, NodeStyleConfig, NodeTypeStyles } from '../types/node-editor';

interface NodeItemProps {
  node: StoryNode;
  selected?: boolean;
  style?: React.CSSProperties;
  onClick?: (node: StoryNode) => void;
  onDoubleClick?: (node: StoryNode) => void;
  theme?: 'light' | 'dark';
}

// 节点类型样式配置
const nodeTypeStyles: NodeTypeStyles = {
  root: {
    backgroundColor: '#667eea',
    borderColor: '#5568d3',
    textColor: '#ffffff',
    fontSize: 18,
    padding: 16,
    borderRadius: 12
  },
  story: {
    backgroundColor: '#764ba2',
    borderColor: '#643a82',
    textColor: '#ffffff',
    fontSize: 16,
    padding: 14,
    borderRadius: 10
  },
  chapter: {
    backgroundColor: '#f093fb',
    borderColor: '#d77aed',
    textColor: '#ffffff',
    fontSize: 15,
    padding: 12,
    borderRadius: 8
  },
  scene: {
    backgroundColor: '#4facfe',
    borderColor: '#3b8cd4',
    textColor: '#ffffff',
    fontSize: 14,
    padding: 12,
    borderRadius: 8
  },
  character: {
    backgroundColor: '#43e97b',
    borderColor: '#38c980',
    textColor: '#ffffff',
    fontSize: 14,
    padding: 12,
    borderRadius: 50  // 圆形
  },
  location: {
    backgroundColor: '#fa709a',
    borderColor: '#e85d8f',
    textColor: '#ffffff',
    fontSize: 14,
    padding: 12,
    borderRadius: 8
  },
  item: {
    backgroundColor: '#fee140',
    borderColor: '#fccb30',
    textColor: '#333333',
    fontSize: 13,
    padding: 10,
    borderRadius: 6
  },
  choice: {
    backgroundColor: '#30cfd0',
    borderColor: '#28b8bd',
    textColor: '#ffffff',
    fontSize: 13,
    padding: 10,
    borderRadius: 8
  }
};

// 节点图标映射
const nodeIcons: Record<NodeType, string> = {
  root: '🌟',
  story: '📖',
  chapter: '📑',
  scene: '🎬',
  character: '👤',
  location: '🏠',
  item: '🎁',
  choice: '🔀'
};

// 节点状态颜色
const statusColors = {
  draft: { bg: '#f4f4f4', border: '#d4d4d8' },
  'in-progress': { bg: '#fef3c7', border: '#fbbf24' },
  completed: { bg: '#bbf7d0', border: '#34d399' },
  archived: { bg: '#e5e7eb', border: '#9ca3af' }
};

const NodeItem: React.FC<NodeItemProps> = ({
  node,
  selected = false,
  style = {},
  onClick,
  onDoubleClick,
  theme = 'dark'
}) => {
  // 获取节点样式
  const baseStyle = useMemo(() => {
    const typeStyle = nodeTypeStyles[node.type] || nodeTypeStyles.scene;
    const statusColor = statusColors[node.status];

    return {
      position: 'absolute',
      left: `${node.position.x}px`,
      top: `${node.position.y}px`,
      width: node.size?.width || (typeStyle.fontSize * 12 + typeStyle.padding * 2),
      height: node.size?.height || (typeStyle.fontSize * 4 + typeStyle.padding * 2),
      backgroundColor: typeStyle.backgroundColor,
      border: selected
        ? `3px solid ${theme === 'dark' ? '#fff' : '#000'}`
        : `2px solid ${typeStyle.borderColor}`,
      borderRadius: typeStyle.borderRadius,
      color: typeStyle.textColor,
      fontSize: `${typeStyle.fontSize}px`,
      padding: `${typeStyle.padding}px`,
      cursor: 'pointer',
      boxShadow: selected
        ? '0 8px 16px rgba(0,0,0,0.3)'
        : '0 4px 8px rgba(0,0,0,0.1)',
      transition: 'all 0.2s',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '8px',
      userSelect: 'none',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap',
      ...style
    };
  }, [node, selected, theme, style]);

  // 处理点击
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick?.(node);
  };

  // 处理双击
  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDoubleClick?.(node);
  };

  // 获取节点图标
  const icon = useMemo(() => nodeIcons[node.type] || '📄', [node.type]);

  return (
    <div
      style={baseStyle}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'scale(1.05)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
      }}
    >
      {/* 节点图标 */}
      <div style={{ fontSize: '24px' }}>
        {icon}
      </div>

      {/* 节点标题 */}
      <div
        style={{
          fontSize: '14px',
          fontWeight: 'bold',
          textAlign: 'center',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: '100%'
        }}
      >
        {node.title}
      </div>

      {/* 节点类型标签 */}
      <div
        style={{
          fontSize: '10px',
          opacity: 0.8,
          textTransform: 'uppercase' as const
        }}
      >
        {node.type}
      </div>

      {/* 节点状态指示器 */}
      <div
        style={{
          position: 'absolute',
          top: '6px',
          right: '6px',
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: statusColors[node.status]?.bg || '#ccc',
          border: `1px solid ${statusColors[node.status]?.border || '#999'}`
        }}
        title={node.status}
      />
    </div>
  );
};

export default NodeItem;
