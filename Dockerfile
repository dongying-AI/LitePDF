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

# Nginx 配置
RUN mkdir -p /etc/nginx/conf.d && \
    echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

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
