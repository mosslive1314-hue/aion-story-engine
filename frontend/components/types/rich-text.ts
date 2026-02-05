/**
 * 富文本编辑器类型定义
 */

import { CSSProperties } from 'react';

// 编辑器模式
export type EditorMode = 'write' | 'preview' | 'split';

// Markdown块类型
export type MarkdownBlockType =
  | 'paragraph'
  | 'heading1'
  | 'heading2'
  | 'heading3'
  | 'heading4'
  | 'heading5'
  | 'heading6'
  | 'code'
  | 'quote'
  | 'bullet'
  | 'numbered'
  | 'task'
  | 'divider'
  | 'image'
  | 'link';

// 工具栏按钮
export interface ToolbarButton {
  id: string;
  label: string;
  icon: string;
  type: MarkdownBlockType;
  shortcut?: string;
  markdown?: string;
}

// 编辑器状态
export interface EditorState {
  content: string;
  mode: EditorMode;
  isFullscreen: boolean;
  wordCount: number;
  lineCount: number;
  cursorPosition: { line: number; column: number };
}

// 编辑器属性
export interface RichTextEditorProps {
  initialValue?: string;
  placeholder?: string;
  readOnly?: boolean;
  maxHeight?: string | number;
  theme?: 'light' | 'dark';
  onChange?: (content: string) => void;
  onSave?: (content: string) => void;
  onWordCountChange?: (count: number) => void;
  className?: string;
  style?: CSSProperties;
}

// Markdown渲染选项
export interface MarkdownOptions {
  remarkPlugins?: any[];
  rehypePlugins?: any[];
  disallowedElements?: string[];
  skipHtml?: boolean;
}

// 统计信息
export interface EditorStats {
  words: number;
  characters: number;
  lines: number;
  paragraphs: number;
  readingTime: number; // 分钟
}

// 图片信息
export interface ImageInfo {
  url: string;
  alt: string;
  title?: string;
  width?: number;
  height?: number;
}

// 链接信息
export interface LinkInfo {
  url: string;
  title?: string;
}
