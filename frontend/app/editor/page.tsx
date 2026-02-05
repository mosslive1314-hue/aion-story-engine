/**
 * 实时协作编辑器演示页面
 */

'use client';

import React, { useState } from 'react';
import RealtimeEditor from '../../../components/RealtimeEditor';

export default function CollaborativeEditorPage() {
  const [userName, setUserName] = useState('用户' + Math.floor(Math.random() * 1000));
  const [documentId, setDocumentId] = useState('demo-doc');
  const [joined, setJoined] = useState(false);

  const handleJoin = () => {
    if (userName.trim() && documentId.trim()) {
      setJoined(true);
    }
  };

  if (!joined) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '40px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          maxWidth: '500px',
          width: '100%'
        }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            marginBottom: '10px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🌌 实时协作编辑器
          </h1>
          <p style={{
            color: '#666',
            marginBottom: '30px',
            fontSize: '14px'
          }}>
            体验多用户实时协作编辑的强大功能
          </p>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#333'
            }}>
              您的姓名
            </label>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="输入您的姓名"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '16px',
                outline: 'none',
                transition: 'border-color 0.3s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div style={{ marginBottom: '30px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#333'
            }}>
              文档 ID
            </label>
            <input
              type="text"
              value={documentId}
              onChange={(e) => setDocumentId(e.target.value)}
              placeholder="输入文档ID"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '16px',
                outline: 'none',
                transition: 'border-color 0.3s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <button
            onClick={handleJoin}
            disabled={!userName.trim() || !documentId.trim()}
            style={{
              width: '100%',
              padding: '14px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
            }}
          >
            🚀 加入协作编辑
          </button>

          <div style={{
            marginTop: '30px',
            padding: '16px',
            background: '#f8f9fa',
            borderRadius: '8px',
            borderLeft: '4px solid #667eea'
          }}>
            <h3 style={{
              fontSize: '14px',
              fontWeight: '600',
              marginBottom: '8px',
              color: '#333'
            }}>
              ✨ 功能特性
            </h3>
            <ul style={{
              fontSize: '13px',
              color: '#666',
              paddingLeft: '20px',
              lineHeight: '1.8'
            }}>
              <li>实时同步编辑</li>
              <li>多用户在线显示</li>
              <li>光标位置实时显示</li>
              <li>冲突自动解决</li>
              <li>优雅的视觉反馈</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#f5f7fa'
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        padding: '16px 24px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            margin: 0
          }}>
            🌌 AION 实时协作编辑器
          </h1>
          <p style={{ fontSize: '14px', color: '#666', margin: '4px 0 0 0' }}>
            欢迎，<strong>{userName}</strong> | 文档 ID: <code>{documentId}</code>
          </p>
        </div>
        <button
          onClick={() => setJoined(false)}
          style={{
            padding: '8px 16px',
            background: '#f8f9fa',
            border: '1px solid #e0e0e0',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = '#e9ecef'}
          onMouseLeave={(e) => e.currentTarget.style.background = '#f8f9fa'}
        >
          ← 返回
        </button>
      </div>

      {/* Editor Container */}
      <div style={{
        flex: 1,
        padding: '24px',
        overflow: 'auto'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          height: '100%'
        }}>
          <RealtimeEditor
            documentId={documentId}
            userId={userName.replace(/\s+/g, '-').toLowerCase()}
            username={userName}
            initialContent={`# 欢迎使用 AION 实时协作编辑器！

这是一个实时协作编辑的演示页面。您可以：

1. 在此处输入内容
2. 邀请其他人加入同一个文档ID来协作编辑
3. 看到实时的光标位置和用户活动
4. 体验无缝的冲突解决

## 开始编写您的故事吧！✨

当前用户: ${userName}
文档ID: ${documentId}

---
`}
          />
        </div>
      </div>

      {/* Footer */}
      <div style={{
        background: 'white',
        padding: '12px 24px',
        textAlign: 'center',
        fontSize: '12px',
        color: '#999',
        borderTop: '1px solid #e0e0e0'
      }}>
        AION Story Engine - Phase 6.2 | 实时协作系统 © 2026
      </div>
    </div>
  );
}
