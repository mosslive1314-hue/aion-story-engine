/**
 * 富文本编辑器组件
 * 支持Markdown编辑和实时预览
 */

'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import EditorToolbar from './EditorToolbar';
import MarkdownPreview from './MarkdownPreview';
import type { RichTextEditorProps, EditorMode, EditorStats } from './types/rich-text';

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  initialValue = '',
  placeholder = '开始编写你的故事...\n\n支持Markdown语法：# 标题、**粗体**、*斜体*、`代码`等',
  readOnly = false,
  maxHeight,
  theme = 'dark',
  onChange,
  onSave,
  onWordCountChange,
  className = '',
  style = {}
}) => {
  // 状态
  const [content, setContent] = useState<string>(initialValue);
  const [mode, setMode] = useState<EditorMode>('split');
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [stats, setStats] = useState<EditorStats>({
    words: 0,
    characters: 0,
    lines: 0,
    paragraphs: 0,
    readingTime: 0
  });

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 计算统计信息
  const calculateStats = useCallback((text: string): EditorStats => {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const characters = text.length;
    const lines = text.split('\n').length;
    const paragraphs = text.trim() ? text.split(/\n\n+/).length : 0;
    const readingTime = Math.ceil(words / 200); // 假设每分钟200字

    return { words, characters, lines, paragraphs, readingTime };
  }, []);

  // 更新统计信息
  useEffect(() => {
    const newStats = calculateStats(content);
    setStats(newStats);
    onWordCountChange?.(newStats.words);
  }, [content, calculateStats, onWordCountChange]);

  // 处理内容变更
  const handleContentChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    onChange?.(newContent);
  }, [onChange]);

  // 处理Markdown插入
  const handleInsertMarkdown = useCallback((markdown: string) => {
    if (!textareaRef.current) return;

    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);
    const textBefore = content.substring(0, start);
    const textAfter = content.substring(end);

    // 智能插入
    let newText: string;
    let newCursorPosition: number;

    if (markdown === '[' || markdown === '![') {
      // 链接或图片
      const isImage = markdown === '![[';
      const linkText = isImage ? 'alt' : selectedText || 'link text';
      const url = 'url';
      newText = `${textBefore}${isImage ? '![' : '['}${linkText}](${url})${textAfter}`;
      newCursorPosition = start + (isImage ? '!['.length : '['.length) + linkText.length;
    } else {
      // 其他Markdown
      newText = textBefore + markdown + selectedText + textAfter;
      newCursorPosition = start + markdown.length;
    }

    setContent(newText);
    onChange?.(newText);

    // 恢复焦点和光标位置
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(newCursorPosition, newCursorPosition);
    }, 0);
  }, [content, onChange]);

  // 处理快捷键
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl/Cmd + S: 保存
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      onSave?.(content);
      return;
    }

    // Ctrl/Cmd + B: 粗体
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
      e.preventDefault();
      handleInsertMarkdown('**');
      return;
    }

    // Ctrl/Cmd + I: 斜体
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
      e.preventDefault();
      handleInsertMarkdown('*');
      return;
    }

    // Ctrl/Cmd + K: 链接
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      handleInsertMarkdown('[');
      return;
    }

    // Tab: 插入缩进
    if (e.key === 'Tab') {
      e.preventDefault();
      handleInsertMarkdown('    ');
      return;
    }

    // Esc: 退出全屏
    if (e.key === 'Escape' && isFullscreen) {
      setIsFullscreen(false);
    }
  }, [content, handleInsertMarkdown, isFullscreen, onSave]);

  // 处理全屏切换
  const handleToggleFullscreen = useCallback(() => {
    setIsFullscreen(!isFullscreen);
  }, [isFullscreen]);

  // 容器样式
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    height: isFullscreen ? '100vh' : 'auto',
    maxHeight: maxHeight,
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    borderRadius: '8px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    overflow: 'hidden',
    ...style
  };

  // 编辑区样式
  const editorStyle: React.CSSProperties = {
    flex: 1,
    display: mode === 'preview' ? 'none' : 'block',
    minHeight: '400px',
    padding: '20px',
    fontSize: '16px',
    lineHeight: '1.8',
    fontFamily: 'monospace',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    border: 'none',
    resize: 'none',
    outline: 'none',
    overflow: 'auto'
  };

  // 分屏容器样式
  const splitContainerStyle: React.CSSProperties = {
    display: 'flex',
    flex: 1,
    overflow: 'hidden'
  };

  // 统计信息样式
  const statsStyle: React.CSSProperties = {
    display: 'flex',
    gap: '16px',
    padding: '8px 16px',
    fontSize: '12px',
    color: theme === 'dark' ? '#a1a1aa' : '#71717a',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
    borderTop: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`
  };

  return (
    <div
      className={`rich-text-editor ${className}`}
      style={containerStyle}
    >
      {/* 工具栏 */}
      <EditorToolbar
        mode={mode}
        onModeChange={setMode}
        onInsertMarkdown={handleInsertMarkdown}
        onToggleFullscreen={handleToggleFullscreen}
        isFullscreen={isFullscreen}
        theme={theme}
      />

      {/* 主内容区 */}
      {mode === 'split' ? (
        <div style={splitContainerStyle}>
          {/* 编辑区 */}
          <textarea
            ref={textareaRef}
            value={content}
            onChange={handleContentChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            readOnly={readOnly}
            style={{
              ...editorStyle,
              flex: 1,
              borderRight: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`
            }}
          />

          {/* 预览区 */}
          <div style={{ flex: 1, overflow: 'auto' }}>
            <MarkdownPreview content={content} theme={theme} />
          </div>
        </div>
      ) : mode === 'write' ? (
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          readOnly={readOnly}
          style={editorStyle}
        />
      ) : (
        <div style={{ flex: 1, overflow: 'auto' }}>
          <MarkdownPreview content={content} theme={theme} />
        </div>
      )}

      {/* 统计信息栏 */}
      <div style={statsStyle}>
        <span>📝 {stats.words} 词</span>
        <span>📄 {stats.characters} 字符</span>
        <span>📃 {stats.lines} 行</span>
        <span>📑 {stats.paragraphs} 段落</span>
        <span>⏱️ {stats.readingTime} 分钟阅读</span>
      </div>
    </div>
  );
};

export default RichTextEditor;
