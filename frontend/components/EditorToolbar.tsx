/**
 * 编辑器工具栏组件
 * 提供Markdown格式化快捷按钮
 */

'use client';

import React, { useCallback } from 'react';
import type { ToolbarButton, EditorMode } from './types/rich-text';

interface EditorToolbarProps {
  mode: EditorMode;
  onModeChange: (mode: EditorMode) => void;
  onInsertMarkdown: (markdown: string) => void;
  onToggleFullscreen?: () => void;
  isFullscreen?: boolean;
  theme?: 'light' | 'dark';
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({
  mode,
  onModeChange,
  onInsertMarkdown,
  onToggleFullscreen,
  isFullscreen = false,
  theme = 'dark'
}) => {
  // 工具栏按钮定义
  const toolbarButtons: ToolbarButton[] = [
    { id: 'h1', label: '标题1', icon: 'H1', type: 'heading1', markdown: '# ', shortcut: 'Ctrl+Alt+1' },
    { id: 'h2', label: '标题2', icon: 'H2', type: 'heading2', markdown: '## ', shortcut: 'Ctrl+Alt+2' },
    { id: 'h3', label: '标题3', icon: 'H3', type: 'heading3', markdown: '### ', shortcut: 'Ctrl+Alt+3' },
    { id: 'bold', label: '粗体', icon: 'B', type: 'paragraph', markdown: '**', shortcut: 'Ctrl+B' },
    { id: 'italic', label: '斜体', icon: 'I', type: 'paragraph', markdown: '*', shortcut: 'Ctrl+I' },
    { id: 'code', label: '代码', icon: '</>', type: 'code', markdown: '`', shortcut: 'Ctrl+`' },
    { id: 'quote', label: '引用', icon: '"', type: 'quote', markdown: '> ', shortcut: 'Ctrl+Shift+>' },
    { id: 'bullet', label: '无序列表', icon: '•', type: 'bullet', markdown: '- ', shortcut: 'Ctrl+Shift+8' },
    { id: 'numbered', label: '有序列表', icon: '1.', type: 'numbered', markdown: '1. ', shortcut: 'Ctrl+Shift+7' },
    { id: 'task', label: '任务列表', icon: '☐', type: 'task', markdown: '- [ ] ', shortcut: 'Ctrl+Shift+T' },
    { id: 'link', label: '链接', icon: '🔗', type: 'link', markdown: '[', shortcut: 'Ctrl+K' },
    { id: 'image', label: '图片', icon: '🖼', type: 'image', markdown: '![', shortcut: 'Ctrl+Shift+I' },
    { id: 'divider', label: '分隔线', icon: '—', type: 'divider', markdown: '\n---\n', shortcut: 'Ctrl+Shift+-' },
  ];

  // 处理按钮点击
  const handleButtonClick = useCallback((button: ToolbarButton) => {
    onInsertMarkdown(button.markdown || '');
  }, [onInsertMarkdown]);

  // 处理快捷键
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const key = e.key;
    const ctrl = e.ctrlKey || e.metaKey;
    const shift = e.shiftKey;
    const alt = e.altKey;

    // 快捷键映射
    const shortcuts: Record<string, string> = {
      'b': '**',  // Ctrl+B - 粗体
      'i': '*',   // Ctrl+I - 斜体
      'k': '[',   // Ctrl+K - 链接
    };

    if (ctrl && !shift && !alt && shortcuts[key]) {
      e.preventDefault();
      onInsertMarkdown(shortcuts[key]);
    }

    if (ctrl && alt && key === '1') {
      e.preventDefault();
      onInsertMarkdown('# ');
    }

    if (ctrl && alt && key === '2') {
      e.preventDefault();
      onInsertMarkdown('## ');
    }

    if (ctrl && alt && key === '3') {
      e.preventDefault();
      onInsertMarkdown('### ');
    }
  }, [onInsertMarkdown]);

  // 样式
  const toolbarStyle: React.CSSProperties = {
    display: 'flex',
    gap: '8px',
    padding: '12px 16px',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
    borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'`,
    alignItems: 'center',
    flexWrap: 'wrap'
  };

  const buttonStyle = (isActive: boolean): React.CSSProperties => ({
    padding: '6px 12px',
    backgroundColor: isActive
      ? theme === 'dark' ? '#667eea' : '#4f46e5'
      : theme === 'dark' ? '#3f3f46' : '#e4e4e7',
    color: isActive ? '#ffffff' : theme === 'dark' ? '#e4e4e7' : '#18181b',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s',
    minWidth: '36px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  });

  const modeButtonStyle = (activeMode: EditorMode): React.CSSProperties => ({
    ...buttonStyle(mode === activeMode),
    textTransform: 'uppercase',
    fontSize: '12px',
    padding: '8px 16px'
  });

  return (
    <div style={toolbarStyle}>
      {/* 模式切换按钮 */}
      <div style={{ display: 'flex', gap: '4px', marginRight: '16px' }}>
        <button
          style={modeButtonStyle('write')}
          onClick={() => onModeChange('write')}
          title="只编辑模式 (Ctrl+Shift+W)"
        >
          ✏️ 编辑
        </button>
        <button
          style={modeButtonStyle('preview')}
          onClick={() => onModeChange('preview')}
          title="只预览模式 (Ctrl+Shift+P)"
        >
          👁️ 预览
        </button>
        <button
          style={modeButtonStyle('split')}
          onClick={() => onModeChange('split')}
          title="分屏模式 (Ctrl+Shift+S)"
        >
          ⚖️ 分屏
        </button>
      </div>

      {/* 分隔线 */}
      <div style={{
        width: '1px',
        height: '32px',
        backgroundColor: theme === 'dark' ? '#3f3f46' : '#d4d4d8',
        marginRight: '16px'
      }} />

      {/* 格式化按钮 */}
      <div style={{ display: 'flex', gap: '4px', flex: 1 }}>
        {toolbarButtons.map((button) => (
          <button
            key={button.id}
            style={buttonStyle(false)}
            onClick={() => handleButtonClick(button)}
            title={`${button.label} (${button.shortcut})`}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {button.icon}
          </button>
        ))}
      </div>

      {/* 分隔线 */}
      <div style={{
        width: '1px',
        height: '32px',
        backgroundColor: theme === 'dark' ? '#3f3f46' : '#d4d4d8',
        marginRight: '16px'
      }} />

      {/* 全屏按钮 */}
      {onToggleFullscreen && (
        <button
          style={buttonStyle(isFullscreen)}
          onClick={onToggleFullscreen}
          title={isFullscreen ? '退出全屏 (Esc)' : '全屏模式 (F11)'}
        >
          {isFullscreen ? '⛶' : '⛶'}
        </button>
      )}
    </div>
  );
};

export default EditorToolbar;
