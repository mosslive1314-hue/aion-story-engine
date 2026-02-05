/**
 * WebSocket 测试客户端
 *
 * 用于测试实时协作编辑器的简单客户端
 */

const WebSocket = require('ws');

class RealtimeEditorClient {
  constructor(serverUrl, documentId, userId, username) {
    this.serverUrl = serverUrl;
    this.documentId = documentId;
    this.userId = userId;
    this.username = username;
    this.ws = null;
    this.color = this.generateUserColor(userId);
  }

  // 生成用户颜色
  generateUserColor(userId) {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
      '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
      '#F8B739', '#52B788', '#E76F51', '#3A86FF'
    ];
    const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }

  // 连接服务器
  connect() {
    return new Promise((resolve, reject) => {
      console.log(`\n🔌 连接到 ${this.serverUrl}...`);

      this.ws = new WebSocket(this.serverUrl);

      this.ws.on('open', () => {
        console.log('✅ WebSocket 连接成功');

        // 加入房间
        const joinMessage = {
          type: 'join',
          room_id: this.documentId,
          user_id: this.userId,
          data: {
            user: {
              user_id: this.userId,
              username: this.username,
              color: this.color
            }
          }
        };

        this.send(joinMessage);
        console.log(`📥 已加入房间: ${this.documentId}`);
        resolve();
      });

      this.ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          this.handleMessage(message);
        } catch (error) {
          console.error('❌ 消息解析错误:', error);
        }
      });

      this.ws.on('error', (error) => {
        console.error('❌ WebSocket 错误:', error.message);
        reject(error);
      });

      this.ws.on('close', () => {
        console.log('🔌 WebSocket 连接已关闭');
      });
    });
  }

  // 发送消息
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  // 处理消息
  handleMessage(message) {
    switch (message.type) {
      case 'join':
        console.log(`\n📥 收到欢迎消息:`);
        console.log(`   房间: ${message.data.room?.name || 'Unknown'}`);
        console.log(`   用户数: ${message.data.users?.length || 0}`);
        break;

      case 'presence':
        if (message.data.action === 'user_joined') {
          console.log(`\n👤 用户加入: ${message.data.user.username}`);
        } else if (message.data.action === 'user_left') {
          console.log(`\n👋 用户离开: ${message.user_id}`);
        }
        break;

      case 'cursor':
        console.log(`\n📍 光标更新: ${message.user_id} -> 位置 ${message.data.cursor_position}`);
        break;

      case 'change':
        console.log(`\n✏️  内容变更: ${message.user_id}`);
        console.log(`   操作: ${JSON.stringify(message.data.operation)}`);
        break;

      case 'sync':
        console.log(`\n🔄 同步消息: ${JSON.stringify(message.data)}`);
        break;

      case 'ping':
        // 自动回复 pong
        this.send({
          type: 'pong',
          data: { timestamp: new Date().toISOString() }
        });
        break;

      default:
        console.log(`\n📨 收到消息: ${message.type}`);
    }
  }

  // 模拟编辑
  simulateEdit(content, delay = 2000) {
    setTimeout(() => {
      console.log(`\n✍️  发送编辑操作...`);
      const operation = {
        type: 'insert',
        position: 0,
        content: content,
        user_id: this.userId
      };

      this.send({
        type: 'change',
        data: { operation }
      });

      console.log(`   内容: "${content}"`);
    }, delay);
  }

  // 发送光标位置
  sendCursor(position) {
    this.send({
      type: 'cursor',
      data: { cursor_position: position }
    });
  }

  // 断开连接
  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// 命令行使用示例
function main() {
  const args = process.argv.slice(2);

  if (args.length < 3) {
    console.log(`
🌌 实时编辑器测试客户端

用法:
  node test_client.js <serverUrl> <documentId> <userId> <username>

示例:
  node test_client.js ws://localhost:8765 demo-doc user1 "张三"
  node test_client.js ws://localhost:8765 my-story story-123 "李四"

参数:
  serverUrl   - WebSocket 服务器地址 (默认: ws://localhost:8765)
  documentId  - 文档 ID
  userId      - 用户 ID
  username    - 用户名
    `);
    process.exit(1);
  }

  const [serverUrl, documentId, userId, ...usernameParts] = args;
  const username = usernameParts.join(' ');

  const client = new RealtimeEditorClient(
    serverUrl,
    documentId,
    userId,
    username
  );

  // 连接并模拟编辑
  client.connect()
    .then(() => {
      console.log('\n✨ 开始测试...');
      console.log('按 Ctrl+C 退出\n');

      // 模拟一些编辑操作
      setTimeout(() => client.simulateEdit('Hello'), 1000);
      setTimeout(() => client.simulateEdit(' World'), 3000);
      setTimeout(() => client.simulateEdit('!'), 5000);

      // 定期发送光标位置
      let cursorPos = 0;
      setInterval(() => {
        cursorPos = (cursorPos + 1) % 20;
        client.sendCursor(cursorPos);
      }, 1000);
    })
    .catch((error) => {
      console.error('连接失败:', error);
      process.exit(1);
    });

  // 优雅关闭
  process.on('SIGINT', () => {
    console.log('\n\n👋 正在关闭连接...');
    client.disconnect();
    setTimeout(() => {
      process.exit(0);
    }, 500);
  });
}

if (require.main === module) {
  main();
}

module.exports = RealtimeEditorClient;
