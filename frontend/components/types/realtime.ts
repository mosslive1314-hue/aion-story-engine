/**
 * WebSocket 实时通信类型定义
 */

export enum MessageType {
  JOIN = 'join',
  LEAVE = 'leave',
  UPDATE = 'update',
  CURSOR = 'cursor',
  SELECTION = 'selection',
  CHANGE = 'change',
  PING = 'ping',
  PONG = 'pong',
  ERROR = 'error',
  PRESENCE = 'presence',
  SYNC = 'sync'
}

export interface User {
  user_id: string;
  username: string;
  color: string;
  cursor_position?: {
    line: number;
    column: number;
  };
  selection?: {
    start: number;
    end: number;
  };
  last_seen: Date;
}

export interface Room {
  room_id: string;
  name: string;
  users: Map<string, User>;
  created_at: Date;
  user_count: number;
}

export interface WebSocketMessage {
  type: MessageType;
  room_id: string;
  user_id: string;
  data: any;
  timestamp: Date;
}

export interface Operation {
  id: string;
  type: 'insert' | 'delete' | 'update';
  position: number;
  user_id: string;
  content?: string;
  length: number;
  timestamp: Date;
  version: number;
  branch_id?: string;
  base_version?: number;
  undo_of?: string;
  redo_of?: string;
  transformed_from?: string;
  metadata?: Record<string, any>;
}

export interface DocumentState {
  content: string;
  version: number;
  operations: Operation[];
  last_modified: Date;
}

export interface Conflict {
  operation1_id: string;
  operation2_id: string;
  position: number;
  type: string;
  resolved: boolean;
}

export interface PresenceStatus {
  status: 'online' | 'away' | 'busy' | 'offline';
  last_seen: Date;
  activity: 'typing' | 'editing' | 'viewing' | 'idle';
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  user_id: string;
  room_id?: string;
  read: boolean;
  created_at: Date;
  expires_at?: Date;
}

export interface CursorPosition {
  line: number;
  column: number;
  position: number;
}

export interface SelectionRange {
  start: number;
  end: number;
  user_id: string;
}

export interface CollaborativeEdit {
  operation: Operation;
  user_id: string;
  timestamp: Date;
}
