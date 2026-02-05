/**
 * 实时协作编辑器组件
 *
 * 提供多用户实时协作编辑体验，包括：
 * - 实时同步编辑
 * - 光标位置显示
 * - 用户在线状态
 * - 冲突解决
 */

'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { User, RemoteCursor } from './types/realtime';
import { useWebSocket } from './useWebSocket';

interface RealtimeEditorProps {
  documentId: string;
  userId: string;
  username: string;
  initialContent?: string;
  websocketUrl?: string;
  onContentChange?: (content: string) => void;
}

export const RealtimeEditor: React.FC<RealtimeEditorProps> = ({
  documentId,
  userId,
  username,
  initialContent = '',
  websocketUrl = 'ws://localhost:8765',
  onContentChange
}) => {
  const [content, setContent] = useState(initialContent);
  const [version, setVersion] = useState(1);
  const [remoteCursors, setRemoteCursors] = useState<Map<string, RemoteCursor>>(new Map());
  const [remoteSelections, setRemoteSelections] = useState<Map<string, any>>(new Map());

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lastSyncedContentRef = useRef<string>(initialContent);

  // 使用 WebSocket Hook
  const {
    connected,
    connectionStatus,
    remoteUsers,
    sendCursorPosition,
    sendChange,
    sendSelection
  } = useWebSocket({
    documentId,
    userId,
    username,
    websocketUrl,
    onCursorChange: (data) => {
      if (data.cursor_position !== undefined) {
        handleRemoteCursor(data);
      }
    },
    onContentChange: (data) => {
      handleRemoteChange(data);
    }
  });

  // 处理远程光标
  const handleRemoteCursor = useCallback((data: any) => {
    const { cursor_position, username, color } = data;
    if (!cursor_position) return;

    const textarea = textareaRef.current;
    if (!textarea) return;

    // 计算光标在文本中的位置
    const lines = content.substring(0, cursor_position).split('\n');
    const line = lines.length - 1;
    const column = lines[lines.length - 1].length;

    setRemoteCursors(prev => {
      const updated = new Map(prev);
      updated.set(data.user_id || 'unknown', {
        userId: data.user_id || 'unknown',
        username,
        color,
        position: cursor_position,
        line,
        column
      });
      return updated;
    });
  }, [content]);

  // 处理远程变更
  const handleRemoteChange = useCallback((data: any) => {
    // TODO: 实现操作变换和冲突解决
    console.log('Remote change:', data);
  }, []);

  // 获取光标在文本中的位置
  const getCursorPosition = useCallback((): number => {
    const textarea = textareaRef.current;
    if (!textarea) return 0;

    return textarea.selectionStart;
  }, []);

  // 处理文本变化
  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    const oldContent = content;

    setContent(newContent);

    // 通知父组件
    if (onContentChange) {
      onContentChange(newContent);
    }

    // 发送变更操作
    const operation = {
      type: 'update',
      old_content: oldContent,
      new_content: newContent,
      timestamp: new Date().toISOString()
    };

    sendChange(operation);
    lastSyncedContentRef.current = newContent;
  }, [content, onContentChange, sendChange]);

  // 处理光标变化
  const handleCursorChange = useCallback(() => {
    const position = getCursorPosition();
    sendCursorPosition(position);
  }, [getCursorPosition, sendCursorPosition]);

  // 处理选择变化
  const handleSelectionChange = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const selection = {
      start: textarea.selectionStart,
      end: textarea.selectionEnd
    };

    sendSelection(selection);
  }, [sendSelection]);

  // 颜色生成器
  const generateUserColor = useCallback((userId: string): string => {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
      '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
      '#F8B739', '#52B788', '#E76F51', '#3A86FF'
    ];
    const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }, []);

  return (
    <div className="realtime-editor">
      {/* 编辑器工具栏 */}
      <div className="editor-toolbar">
        <div className="toolbar-left">
          <span className="editor-title">📝 协作编辑器</span>
          <span className="document-id">文档: {documentId}</span>
        </div>
        <div className="toolbar-right">
          <div className="connection-status">
            <div className={`status-indicator ${connectionStatus}`} />
            <span className="status-text">
              {connectionStatus === 'connected' ? '🟢 已连接' :
               connectionStatus === 'connecting' ? '🟡 连接中...' : '🔴 未连接'}
            </span>
          </div>
        </div>
      </div>

      {/* 用户列表 */}
      <div className="user-list">
        <div className="user-avatars">
          {/* 当前用户 */}
          <div
            className="user-avatar current-user"
            style={{ backgroundColor: generateUserColor(userId) }}
            title={`${username} (你)`}
          >
            {username.charAt(0).toUpperCase()}
          </div>

          {/* 远程用户 */}
          {Array.from(remoteUsers.values()).map((user) => (
            <div
              key={user.user_id}
              className="user-avatar"
              style={{ backgroundColor: user.color }}
              title={`${user.username} (在线)`}
            >
              {user.username.charAt(0).toUpperCase()}
            </div>
          ))}
        </div>
        <div className="user-count">
          {remoteUsers.size + 1} 人在线
        </div>
      </div>

      {/* 编辑器主体 */}
      <div className="editor-container">
        <textarea
          ref={textareaRef}
          className="editor-textarea"
          value={content}
          onChange={handleTextChange}
          onSelect={handleSelectionChange}
          onClick={handleCursorChange}
          onKeyUp={handleCursorChange}
          placeholder="开始协作编辑...邀请其他人一起编辑此文档！"
          spellCheck={false}
        />

        {/* 远程光标 */}
        {Array.from(remoteCursors.values()).map((cursor) => (
          <div
            key={cursor.userId}
            className="remote-cursor"
            style={{
              backgroundColor: cursor.color,
              top: `${cursor.line * 24}px`,
              left: `${cursor.column * 8}px`
            }}
          >
            <div className="cursor-label">{cursor.username}</div>
          </div>
        ))}

        {/* 远程选择 */}
        {Array.from(remoteSelections.entries()).map(([userId, selection]) => (
          <div
            key={userId}
            className="remote-selection"
            style={{
              backgroundColor: 'rgba(66, 133, 244, 0.3)',
              top: `${selection.line * 24}px`,
              left: `${selection.column * 8}px`,
              width: `${selection.width * 8}px`,
              height: '24px'
            }}
          />
        ))}
      </div>

      {/* 编辑器状态栏 */}
      <div className="editor-statusbar">
        <div className="status-left">
          <span>📄 行数: {content.split('\n').length}</span>
          <span className="separator">|</span>
          <span>📝 字符数: {content.length}</span>
          <span className="separator">|</span>
          <span>🔢 版本: {version}</span>
        </div>
        <div className="status-right">
          <span>⏰ 最后同步: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* 样式 */}
      <style jsx>{`
        .realtime-editor {
          display: flex;
          flex-direction: column;
          height: 100%;
          min-height: 600px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          overflow: hidden;
          background: white;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .editor-toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .toolbar-left {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .editor-title {
          font-weight: 600;
          font-size: 16px;
        }

        .document-id {
          font-size: 12px;
          background: rgba(255, 255, 255, 0.2);
          padding: 4px 8px;
          border-radius: 4px;
        }

        .connection-status {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .status-indicator {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }

        .status-indicator.connected {
          background: #28a745;
        }

        .status-indicator.connecting {
          background: #ffc107;
          animation: pulse 1s infinite;
        }

        .status-indicator.disconnected {
          background: #dc3545;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.6;
            transform: scale(1.1);
          }
        }

        .status-text {
          font-size: 13px;
          font-weight: 500;
        }

        .user-list {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 16px;
          background: #f8f9fa;
          border-bottom: 1px solid #e0e0e0;
        }

        .user-avatars {
          display: flex;
          gap: 10px;
        }

        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 600;
          color: white;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
          transition: transform 0.2s;
        }

        .user-avatar:hover {
          transform: scale(1.1);
        }

        .user-avatar.current-user {
          box-shadow: 0 0 0 3px #007bff, 0 2px 8px rgba(0,0,0,0.15);
        }

        .user-count {
          font-size: 13px;
          color: #666;
          font-weight: 500;
        }

        .editor-container {
          flex: 1;
          position: relative;
          overflow: auto;
          background: #fafafa;
        }

        .editor-textarea {
          width: 100%;
          height: 100%;
          padding: 20px;
          border: none;
          outline: none;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
          font-size: 14px;
          line-height: 1.6;
          resize: none;
          background: white;
          color: #1a1a1a;
          transition: background 0.3s;
        }

        .editor-textarea:focus {
          background: #fff;
        }

        .editor-textarea::placeholder {
          color: #adb5bd;
          font-style: italic;
        }

        .remote-cursor {
          position: absolute;
          width: 2px;
          height: 24px;
          pointer-events: none;
          transition: all 0.1s ease;
        }

        .cursor-label {
          position: absolute;
          top: -28px;
          left: -4px;
          font-size: 11px;
          padding: 3px 8px;
          border-radius: 4px;
          color: white;
          white-space: nowrap;
          font-weight: 600;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          animation: fadeIn 0.2s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-5px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .remote-selection {
          position: absolute;
          pointer-events: none;
          border-radius: 2px;
        }

        .editor-statusbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 16px;
          background: #f1f3f5;
          border-top: 1px solid #e0e0e0;
          font-size: 12px;
          color: #666;
        }

        .status-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .separator {
          color: #ced4da;
        }

        .status-right {
          font-size: 11px;
          color: #adb5bd;
        }
      `}</style>
    </div>
  );
};

export default RealtimeEditor;
