# LitePDF — 本地文档处理工具箱

一款纯前端实现的文档处理工具箱，所有文件处理均在浏览器本地完成。支持 PDF、PPT、Word、Excel、EPUB、HTML、Markdown、图片等 20+ 种格式转换与处理。

---

## 功能一览

### 格式互转

| 工具 | 说明 |
|---|---|
| PDF → 图片 | 每页渲染为高清 PNG/JPG |
| PPT → 图片 | 幻灯片导出为图片序列 |
| 图片 → PDF | JPG/PNG/WebP 组合合成 PDF |
| Word → PDF | .docx 本地转换 |
| Excel → PDF | .xlsx 表格渲染输出 |
| PPT → PDF | .pptx 幻灯片无损转换 |
| HTML → PDF | 粘贴代码或上传文件，实时预览后导出 |
| EPUB → PDF / Word | 电子书章节解析，重新排版导出 |
| PDF → Word | 文本提取与基础布局还原 |
| PDF → Excel | 表格结构识别与数据导出 |
| Markdown → PDF | 实时排版编辑器，4 套主题（Apple/Bauhaus/Academic/Tech），导出 PDF/长图 |

### PDF 核心工具

| 工具 | 说明 |
|---|---|
| PDF 压缩 | 低/中/高三档压缩 |
| PDF 合并 | 多文件拖拽排序合并 |
| PDF 拆分 | 按页码范围精确拆分 |
| 全格式水印 | PDF/图片/Office 添加文本或图案水印 |
| 智能脱敏 | 自动识别 + 手动框选涂抹敏感信息，物理级抹除 |
| 内嵌图片提取 | 从 Word/PPT/PDF 解包所有高清原图，打包 ZIP |
| 电子签章 | 本地印章库 + 手写签名，画布直接加盖 |

### OCR 文字识别

| 特性 | 说明 |
|---|---|
| 图片识别 | PNG/JPG/WebP/BMP，中英混合 |
| PDF 识别 | 自动区分文本版与扫描版，多页全量提取 |
| 文本版 PDF | 直接提取文本层，毫秒级，保留行结构 |
| 扫描版 PDF | 逐页渲染后 OCR 识别 |
| 输出格式 | 纯文本 / 保留段落格式（坐标重建） |

### 安全

| 工具 | 说明 |
|---|---|
| PDF 加密 | AES-256-GCM 真实加密，PBKDF2 密钥派生 |
| 权限控制 | 细粒度锁定打印/复制/修改 |
| PDF 解密 | 已知密码移除安全限制 |
| 数字签名 | X.509 证书本地签名 |

### 体验

| 特性 | 说明 |
|---|---|
| 深色/浅色主题 | 持久化 localStorage |
| 中英文双语 | 一键切换 |
| 留言反馈 | 内置留言板，支持回复/删除 |

---

## 技术栈

| 类别 | 技术 |
|---|---|
| 前端 | 原生 HTML + JavaScript + Tailwind CSS |
| PDF | PDF-Lib, PDF.js |
| 文档 | JSZip, SheetJS, marked.js, html2canvas |
| 加密 | Web Crypto API (AES-256-GCM + PBKDF2) |
| 后端 | Node.js (留言), Python Flask (OCR) |
| OCR 引擎 | PaddleOCR (PP-OCRv4, paddle 2.6.2) |
| 部署 | Docker + Docker Compose + Nginx |

---

## 快速开始

### 本地开发

```bash
git clone https://github.com/dongying-AI/LitePDF.git
cd LitePDF

# 1. 启动前端
python -m http.server 8088
# 访问 http://localhost:8088

# 2. 启动留言后端（可选）
node server.js

# 3. 启动 OCR 后端（可选）
pip install paddlepaddle==2.6.2 paddleocr==2.8.1 flask flask-cors pillow numpy
python ocr_server.py
```

### Docker 部署

```bash
# 启动全部服务
docker compose up -d

# 依赖变更后重建
docker compose build --no-cache
docker compose up -d
```

| 服务 | 端口 | 说明 |
|---|---|---|
| 前端 | 8088 | Nginx 静态页面 |
| 留言 API | 3000 | Node.js |
| OCR API | 5000 | Python Flask + PaddleOCR |

---

## 隐私说明

- 所有文件处理均在浏览器本地完成，不上传任何远程服务器
- 加密使用 Web Crypto API，密钥不离开本地
- 留言数据保存在本地 `data/` 目录
- OCR 通过本地 Docker 后端服务完成

## License

MIT
