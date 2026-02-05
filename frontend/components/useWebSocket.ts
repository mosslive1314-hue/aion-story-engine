/**
 * WebSocket 连接管理 Hook
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { MessageType, WebSocketMessage, User } from './types/realtime';

interface UseWebSocketOptions {
  documentId: string;
  userId: string;
  username: string;
  websocketUrl?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onUserJoined?: (user: User) => void;
  onUserLeft?: (userId: string) => void;
  onCursorChange?: (data: any) => void;
  onContentChange?: (data: any) => void;
}

export const useWebSocket = (options: UseWebSocketOptions) => {
  const {
    documentId,
    userId,
    username,
    websocketUrl = 'ws://localhost:8765',
    onMessage,
    onUserJoined,
    onUserLeft,
    onCursorChange,
    onContentChange
  } = options;

  const [connected, setConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [remoteUsers, setRemoteUsers] = useState<Map<string, User>>(new Map());

  const wsRef = useRef<WebSocket | null>(null);

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

  // 连接 WebSocket
  const connect = useCallback(() => {
    try {
      setConnectionStatus('connecting');
      const ws = new WebSocket(websocketUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        setConnectionStatus('connected');

        // 加入房间
        const joinMessage = {
          type: MessageType.JOIN,
          room_id: documentId,
          user_id: userId,
          data: {
            user: {
              user_id: userId,
              username: username,
              color: generateUserColor(userId)
            }
          }
        };
        ws.send(JSON.stringify(joinMessage));
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        setConnectionStatus('disconnected');

        // 自动重连
        setTimeout(() => {
          if (wsRef.current?.readyState === WebSocket.CLOSED) {
            connect();
          }
        }, 3000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  }, [documentId, userId, username, generateUserColor, websocketUrl]);

  // 处理消息
  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case MessageType.JOIN:
        if (message.data?.users) {
          const usersMap = new Map<string, User>();
          message.data.users.forEach((user: User) => {
            usersMap.set(user.user_id, user);
          });
          setRemoteUsers(usersMap);
        }
        break;

      case MessageType.PRESENCE:
        const { action, user } = message.data;
        setRemoteUsers(prev => {
          const updated = new Map(prev);

          if (action === 'user_joined' && user) {
            updated.set(user.user_id, user);
            onUserJoined?.(user);
          } else if (action === 'user_left' && message.user_id) {
            updated.delete(message.user_id);
            onUserLeft?.(message.user_id);
          }

          return updated;
        });
        break;

      case MessageType.CURSOR:
        onCursorChange?.(message.data);
        break;

      case MessageType.CHANGE:
        onContentChange?.(message.data);
        break;
    }

    onMessage?.(message);
  }, [onMessage, onUserJoined, onUserLeft, onCursorChange, onContentChange]);

  // 发送消息
  const sendMessage = useCallback((message: Partial<WebSocketMessage>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        ...message,
        room_id: documentId,
        user_id: userId,
        timestamp: new Date().toISOString()
      }));
    }
  }, [documentId, userId]);

  // 发送光标位置
  const sendCursorPosition = useCallback((position: number) => {
    sendMessage({
      type: MessageType.CURSOR,
      data: {
        cursor_position: position
      }
    });
  }, [sendMessage]);

  // 发送内容变更
  const sendChange = useCallback((operation: any) => {
    sendMessage({
      type: MessageType.CHANGE,
      data: {
        operation
      }
    });
  }, [sendMessage]);

  // 发送选择范围
  const sendSelection = useCallback((selection: { start: number; end: number }) => {
    sendMessage({
      type: MessageType.SELECTION,
      data: {
        selection
      }
    });
  }, [sendMessage]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // 组件挂载时连接
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connected,
    connectionStatus,
    remoteUsers,
    sendMessage,
    sendCursorPosition,
    sendChange,
    sendSelection,
    connect,
    disconnect
  };
};

export default useWebSocket;
