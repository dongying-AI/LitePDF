# LitePDF 一键部署镜像
# 包含 Nginx 前端 + Node.js 后端

FROM node:18-alpine

# 安装 Nginx
RUN apk add --no-cache nginx

# 创建工作目录
WORKDIR /app

# 复制后端代码
COPY server.js ./

# 复制前端文件到 Nginx 目录
COPY index.html /usr/share/nginx/html/

# 创建数据目录
RUN mkdir -p /app/data

# Nginx 配置（/api/ocr 优先 → 5000，/api/ → 3000）
RUN printf 'worker_processes auto;\npid /run/nginx.pid;\nevents { worker_connections 1024; }\nhttp {\n    include /etc/nginx/mime.types;\n    default_type application/octet-stream;\n    sendfile on;\n    keepalive_timeout 65;\n    server {\n        listen 80;\n        server_name localhost;\n        root /usr/share/nginx/html;\n        index index.html;\n        location /api/ocr {\n            proxy_pass http://ocr:5000/ocr;\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n        }\n        location /api/ {\n            proxy_pass http://127.0.0.1:3000;\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n        }\n        location / {\n            try_files $uri $uri/ /index.html;\n        }\n    }\n}\n' > /etc/nginx/nginx.conf

# 启动脚本
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'mkdir -p /app/data' >> /app/start.sh && \
    echo 'node /app/server.js &' >> /app/start.sh && \
    echo 'nginx -g "daemon off;"' >> /app/start.sh && \
    chmod +x /app/start.sh

# 暴露端口
EXPOSE 80 3000

# 启动
CMD ["/app/start.sh"]
