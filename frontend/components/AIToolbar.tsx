/**
 * AI 工具栏组件
 * 提供各种 AI 辅助创作功能
 */

'use client';

import React, { useState, useCallback } from 'react';

interface AIToolbarProps {
  onContentComplete: (context: string) => Promise<string>;
  onTextPolish: (text: string) => Promise<string>;
  onTextExpand: (text: string) => Promise<string>;
  onGenerateDialogue: (character: string, context: string) => Promise<string>;
  onSuggestPlot: (plot: string) => Promise<string[]>;
  theme?: 'light' | 'dark';
  disabled?: boolean;
}

const AIToolbar: React.FC<AIToolbarProps> = ({
  onContentComplete,
  onTextPolish,
  onTextExpand,
  onGenerateDialogue,
  onSuggestPlot,
  theme = 'dark',
  disabled = false
}) => {
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleToolClick = useCallback(async (toolName: string) => {
    if (disabled || loading) return;

    setLoading(true);
    setActiveTool(toolName);

    try {
      // 这里应该触发相应的 AI 功能
      // 实际实现需要与编辑器集成
      console.log(`AI Tool activated: ${toolName}`);

      // 示例：获取选中文本
      const selection = window.getSelection()?.toString() || '';

      if (toolName === 'polish' && selection) {
        await onTextPolish(selection);
      } else if (toolName === 'expand' && selection) {
        await onTextExpand(selection);
      }
    } catch (error) {
      console.error('AI tool error:', error);
    } finally {
      setLoading(false);
      setActiveTool(null);
    }
  }, [disabled, loading, onTextPolish, onTextExpand]);

  const tools = [
    { id: 'complete', label: '✨ 补全', icon: '✨', hint: '智能内容补全' },
    { id: 'polish', label: '🎨 润色', icon: '🎨', hint: '润色优化文本' },
    { id: 'expand', label: '📝 扩写', icon: '📝', hint: '扩写文本内容' },
    { id: 'dialogue', label: '💬 对话', icon: '💬', hint: '生成角色对话' },
    { id: 'plot', label: '🎭 情节', icon: '🎭', hint: '情节建议' },
    { id: 'character', label: '👤 角色', icon: '👤', hint: '创建角色' },
    { id: 'scene', label: '🏞️ 场景', icon: '🏞️', hint: '描述场景' },
    { id: 'opening', label: '📖 开头', icon: '📖', hint: '生成故事开头' },
  ];

  const buttonStyle = (toolId: string) => ({
    padding: '8px 12px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '6px',
    backgroundColor: activeTool === toolId
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      : theme === 'dark' ? '#2d2d2d' : '#ffffff',
    color: activeTool === toolId ? '#ffffff' : theme === 'dark' ? '#e4e4e7' : '#18181b',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: '13px',
    transition: 'all 0.2s ease',
    opacity: disabled ? 0.5 : 1,
  });

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    gap: '8px',
    padding: '12px',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    flexWrap: 'wrap',
  };

  const loadingOverlay: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  };

  const loadingBox: React.CSSProperties = {
    padding: '20px 30px',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
    borderRadius: '8px',
    textAlign: 'center',
  };

  return (
    <>
      <div style={containerStyle}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: theme === 'dark' ? '#e4e4e7' : '#18181b',
          marginRight: '12px',
          display: 'flex',
          alignItems: 'center'
        }}>
          🤖 AI 助手
        </div>

        {tools.map((tool) => (
          <button
            key={tool.id}
            onClick={() => handleToolClick(tool.id)}
            disabled={disabled}
            style={buttonStyle(tool.id)}
            title={tool.hint}
          >
            <span style={{ marginRight: '4px' }}>{tool.icon}</span>
            {tool.label}
          </button>
        ))}

        <div style={{ flex: 1 }} />

        <div style={{
          fontSize: '12px',
          color: theme === 'dark' ? '#a1a1aa' : '#71717a',
          padding: '8px 12px',
          backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
          borderRadius: '6px'
        }}>
          💡 选中文字后使用工具
        </div>
      </div>

      {loading && (
        <div style={loadingOverlay}>
          <div style={loadingBox}>
            <div style={{ fontSize: '24px', marginBottom: '12px' }}>🤖</div>
            <div style={{
              fontSize: '16px',
              fontWeight: '600',
              color: theme === 'dark' ? '#e4e4e7' : '#18181b',
              marginBottom: '8px'
            }}>
              AI 正在创作中...
            </div>
            <div style={{
              fontSize: '14px',
              color: theme === 'dark' ? '#a1a1aa' : '#71717a'
            }}>
              请稍候
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AIToolbar;
