/**
 * LitePDF Message Server
 * 留言后端服务 - 保存留言到本地文件
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;
const MESSAGES_FILE = path.join(__dirname, 'data', 'messages.json');

// 确保留言文件存在
function ensureMessagesFile() {
    if (!fs.existsSync(MESSAGES_FILE)) {
        fs.writeFileSync(MESSAGES_FILE, JSON.stringify({ messages: [] }, null, 2), 'utf8');
        console.log('Created messages.json');
    }
}

// 读取留言
function loadMessages() {
    try {
        const data = fs.readFileSync(MESSAGES_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        console.error('Error loading messages:', err);
        return { messages: [] };
    }
}

// 保存留言
function saveMessages(data) {
    try {
        fs.writeFileSync(MESSAGES_FILE, JSON.stringify(data, null, 2), 'utf8');
        return true;
    } catch (err) {
        console.error('Error saving messages:', err);
        return false;
    }
}

// 生成唯一 ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

    // CORS 头
function setCORSHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
}

// 解析请求体
function parseBody(req, callback) {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
        try {
            callback(null, body ? JSON.parse(body) : {});
        } catch (err) {
            callback(err, null);
        }
    });
}

// 创建服务器
const server = http.createServer((req, res) => {
    setCORSHeaders(res);

    // 处理预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    console.log(`${new Date().toISOString()} - ${req.method} ${pathname}`);

    // GET /api/messages - 获取所有留言
    if (pathname === '/api/messages' && req.method === 'GET') {
        const data = loadMessages();
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify(data));
        return;
    }

    // POST /api/messages - 添加留言
    if (pathname === '/api/messages' && req.method === 'POST') {
        parseBody(req, (err, body) => {
            if (err) {
                res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
                return;
            }

            const { name, content } = body;
            if (!name || !content) {
                res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Name and content are required' }));
                return;
            }

            const data = loadMessages();
            const newMessage = {
                id: generateId(),
                name: name.trim(),
                content: content.trim(),
                timestamp: Date.now(),
                replies: []
            };

            data.messages.unshift(newMessage);

            if (saveMessages(data)) {
                res.writeHead(201, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ success: true, message: newMessage }));
            } else {
                res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Failed to save message' }));
            }
        });
        return;
    }

    // DELETE /api/messages/:id - 删除留言
    if (pathname.startsWith('/api/messages/') && req.method === 'DELETE') {
        const msgId = pathname.split('/')[3];
        const data = loadMessages();
        const initialLength = data.messages.length;

        data.messages = data.messages.filter(m => m.id !== msgId);

        if (data.messages.length === initialLength) {
            res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
            res.end(JSON.stringify({ error: 'Message not found' }));
            return;
        }

        if (saveMessages(data)) {
            res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
            res.end(JSON.stringify({ success: true }));
        } else {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to delete message' }));
        }
        return;
    }

    // POST /api/messages/:id/replies - 添加回复
    if (pathname.startsWith('/api/messages/') && pathname.endsWith('/replies') && req.method === 'POST') {
        const msgId = pathname.split('/')[3];

        parseBody(req, (err, body) => {
            if (err) {
                res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
                return;
            }

            const { name, content } = body;
            if (!content) {
                res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Content is required' }));
                return;
            }

            const data = loadMessages();
            const msg = data.messages.find(m => m.id === msgId);

            if (!msg) {
                res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Message not found' }));
                return;
            }

            const newReply = {
                id: generateId(),
                name: (name || 'Anonymous').trim(),
                content: content.trim(),
                timestamp: Date.now()
            };

            msg.replies.push(newReply);

            if (saveMessages(data)) {
                res.writeHead(201, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ success: true, reply: newReply }));
            } else {
                res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'Failed to save reply' }));
            }
        });
        return;
    }

    // 404
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
});

// 启动服务器
ensureMessagesFile();
server.listen(PORT, () => {
    console.log(`LitePDF Message Server running at http://localhost:${PORT}`);
    console.log(`Messages file: ${MESSAGES_FILE}`);
    console.log('');
    console.log('API Endpoints:');
    console.log('  GET    /api/messages          - Get all messages');
    console.log('  POST   /api/messages          - Add new message');
    console.log('  DELETE /api/messages/:id      - Delete message');
    console.log('  POST   /api/messages/:id/replies - Add reply to message');
});
