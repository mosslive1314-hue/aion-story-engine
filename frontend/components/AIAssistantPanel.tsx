/**
 * AI 助手面板
 * 展示 AI 生成的内容和建议
 */

'use client';

import React, { useState } from 'react';

interface AIAssistantPanelProps {
  suggestions: string[];
  onSelectSuggestion: (suggestion: string) => void;
  onClose?: () => void;
  theme?: 'light' | 'dark';
}

const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
  suggestions,
  onSelectSuggestion,
  onClose,
  theme = 'dark'
}) => {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const handleSuggestionClick = (index: number, suggestion: string) => {
    setSelectedIndex(index);
    onSelectSuggestion(suggestion);
  };

  const containerStyle: React.CSSProperties = {
    position: 'fixed',
    right: '0',
    top: '0',
    width: '400px',
    height: '100vh',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
    borderLeft: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    boxShadow: '-4px 0 12px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1000,
  };

  const headerStyle: React.CSSProperties = {
    padding: '20px',
    borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
  };

  const suggestionCardStyle = (index: number) => ({
    padding: '16px',
    marginBottom: '12px',
    backgroundColor: selectedIndex === index
      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
      : theme === 'dark' ? '#1f1f1f' : '#f4f4f4',
    border: `2px solid ${
      selectedIndex === index
        ? '#667eea'
        : theme === 'dark' ? '#3f3f46' : '#e4e4e7'
    }`,
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  });

  const footerStyle: React.CSSProperties = {
    padding: '16px 20px',
    borderTop: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    fontSize: '12px',
    color: theme === 'dark' ? '#a1a1aa' : '#71717a',
    textAlign: 'center',
  };

  return (
    <div style={containerStyle}>
      {/* 头部 */}
      <div style={headerStyle}>
        <div>
          <h2 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: 'bold',
            color: theme === 'dark' ? '#e4e4e7' : '#18181b'
          }}>
            🤖 AI 建议
          </h2>
          <p style={{
            margin: '4px 0 0 0',
            fontSize: '12px',
            color: theme === 'dark' ? '#a1a1aa' : '#71717a'
          }}>
            {suggestions.length} 个建议
          </p>
        </div>

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

      {/* 内容区 */}
      <div style={contentStyle}>
        {suggestions.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '40px 20px',
            color: theme === 'dark' ? '#71717a' : '#a1a1aa'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤔</div>
            <div style={{ fontSize: '16px', marginBottom: '8px' }}>
              暂无建议
            </div>
            <div style={{ fontSize: '14px' }}>
              使用 AI 工具获取创作建议
            </div>
          </div>
        ) : (
          suggestions.map((suggestion, index) => (
            <div
              key={index}
              onClick={() => handleSuggestionClick(index, suggestion)}
              style={suggestionCardStyle(index)}
            >
              <div style={{
                fontSize: '12px',
                color: theme === 'dark' ? '#a1a1aa' : '#71717a',
                marginBottom: '8px'
              }}>
                建议 {index + 1}
              </div>
              <div style={{
                fontSize: '14px',
                color: theme === 'dark' ? '#e4e4e7' : '#18181b',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap'
              }}>
                {suggestion}
              </div>
            </div>
          ))
        )}
      </div>

      {/* 底部 */}
      <div style={footerStyle}>
        点击建议即可应用到编辑器
      </div>
    </div>
  );
};

export default AIAssistantPanel;
