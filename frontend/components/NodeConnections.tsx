/**
 * 节点连接线组件
 * 显示节点之间的关系
 */

'use client';

import React, { useMemo } from 'react';
import type { NodeConnection, StoryNode } from '../types/node-editor';

interface NodeConnectionsProps {
  connections: NodeConnection[];
  nodes: StoryNode[];
  theme?: 'light' | 'dark';
  style?: React.CSSProperties;
}

const NodeConnections: React.FC<NodeConnectionsProps> = ({
  connections,
  nodes,
  theme = 'dark',
  style = {}
}) => {
  // SVG样式
  const svgStyle: React.CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: 0,
    ...style
  };

  // 生成路径
  const paths = useMemo(() => {
    return connections.map((conn) => {
      const sourceNode = nodes.find(n => n.id === conn.sourceId);
      const targetNode = nodes.find(n => n.id === conn.targetId);

      if (!sourceNode || !targetNode) {
        return null;
      }

      // 计算节点中心点
      const sourceCenter = {
        x: sourceNode.position.x + (sourceNode.size?.width || 150) / 2,
        y: sourceNode.position.y + (sourceNode.size?.height || 80) / 2
      };

      const targetCenter = {
        x: targetNode.position.x + (targetNode.size?.width || 150) / 2,
        y: targetNode.position.y + (targetNode.size?.height || 80) / 2
      };

      // 生成曲线路径
      const deltaX = targetCenter.x - sourceCenter.x;
      const deltaY = targetCenter.y - sourceCenter.y;

      // 使用三次贝塞尔曲线创建平滑连接
      const controlOffset = Math.min(Math.abs(deltaX) * 0.5, 100);

      const pathData = `M ${sourceCenter.x} ${sourceCenter.y}
                       C ${sourceCenter.x + controlOffset} ${sourceCenter.y},
                         ${targetCenter.x - controlOffset} ${targetCenter.y},
                         ${targetCenter.x} ${targetCenter.y}`;

      return {
        ...conn,
        sourceCenter,
        targetCenter,
        pathData,
        color: conn.color || (theme === 'dark' ? '#a1a1aa' : '#71717a')
      };
    }).filter(Boolean);
  }, [connections, nodes, theme]);

  if (paths.length === 0) {
    return null;
  }

  return (
    <svg style={svgStyle}>
      <defs>
        {/* 定义箭头标记 */}
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill={theme === 'dark' ? '#a1a1aa' : '#71717a'}
          />
        </marker>
      </defs>

      {/* 绘制连接线 */}
      {paths.map((path) => (
        <g key={path.id}>
          {/* 线条 */}
          <path
            d={path.pathData}
            stroke={path.color}
            strokeWidth="2"
            fill="none"
            strokeDasharray={path.type === 'dashed' ? '5,5' : path.type === 'dotted' ? '2,2' : undefined}
            markerEnd="url(#arrowhead)"
            opacity={0.6}
          />

          {/* 标签 */}
          {path.label && (
            <text
              x={(path.sourceCenter.x + path.targetCenter.x) / 2}
              y={(path.sourceCenter.y + path.targetCenter.y) / 2 - 10}
              fill={theme === 'dark' ? '#e4e4e7' : '#18181b'}
              fontSize="12"
              textAnchor="middle"
              style={{
                background: theme === 'dark' ? '#1f1f1f' : '#ffffff',
                padding: '2px 6px',
                borderRadius: '4px'
              }}
            >
              {path.label}
            </text>
          )}
        </g>
      ))}
    </svg>
  );
};

export default NodeConnections;
