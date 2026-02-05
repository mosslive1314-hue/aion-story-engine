/**
 * 节点编辑器类型定义
 */

import { CSSProperties } from 'react';

// 节点类型
export type NodeType =
  | 'root'          // 根节点
  | 'story'         // 故事节点
  | 'chapter'       // 章节
  | 'scene'         // 场景
  | 'character'     // 角色
  | 'location'      // 地点
  | 'item'          // 物品
  | 'choice';       // 选择分支

// 节点状态
export type NodeStatus =
  | 'draft'         // 草稿
  | 'in-progress'   // 进行中
  | 'completed'     // 已完成
  | 'archived';     // 已归档

// 节点数据结构
export interface StoryNode {
  id: string;
  type: NodeType;
  title: string;
  description?: string;
  content?: string;
  parentId?: string | null;
  children: string[];  // 子节点ID列表
  position: {
    x: number;
    y: number;
  };
  size?: {
    width: number;
    height: number;
  };
  status: NodeStatus;
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

// 节点连接
export interface NodeConnection {
  id: string;
  sourceId: string;
  targetId: string;
  type?: 'solid' | 'dashed' | 'dotted';
  color?: string;
  label?: string;
}

// 视口状态
export interface ViewportState {
  scale: number;      // 缩放比例
  offset: {          // 偏移量
    x: number;
    y: number;
  };
}

// 选择状态
export interface SelectionState {
  selectedNodes: Set<string>;
  selectedConnections: Set<string>;
  isDragging: boolean;
  dragStart: {
    x: number;
    y: number;
  };
}

// 编辑器属性
export interface NodeEditorProps {
  nodes: StoryNode[];
  connections?: NodeConnection[];
  onNodeChange?: (node: StoryNode) => void;
  onNodeDelete?: (nodeId: string) => void;
  onConnectionAdd?: (connection: NodeConnection) => void;
  onConnectionDelete?: (connectionId: string) => void;
  onNodeSelect?: (nodeId: string | null) => void;
  theme?: 'light' | 'dark';
  className?: string;
  style?: CSSProperties;
}

// 节点样式配置
export interface NodeStyleConfig {
  backgroundColor: string;
  borderColor: string;
  textColor: string;
  fontSize: number;
  padding: number;
  borderRadius: number;
  shadow?: string;
}

// 节点类型样式映射
export type NodeTypeStyles = Record<NodeType, NodeStyleConfig>;

// 画布事件
export interface CanvasEvent {
  type: 'click' | 'dblclick' | 'drag' | 'drop' | 'zoom' | 'pan';
  position: { x: number; y: number };
  target?: string;
  delta?: { x: number; y: number };
}

// 属性面板数据
export interface PropertyPanelData {
  node: StoryNode | null;
  visible: boolean;
  position: {
    x: number;
    y: number;
  };
}

// 布局算法选项
export interface LayoutOptions {
  type: 'tree' | 'force' | 'circle' | 'hierarchy';
  direction?: 'horizontal' | 'vertical';
  spacing: {
    x: number;
    y: number;
  };
  nodeSize: {
    width: number;
    height: number;
  };
}
