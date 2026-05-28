# LitePDF - 本地文档处理工具箱

一款纯前端实现的本地文档处理工具箱，支持 PDF、Markdown、HTML、EPUB、图片、Word、Excel、PPT 等多种格式的转换与处理。所有文件处理均在浏览器本地完成，无需上传到云端服务器。

## 功能特性

### 格式互转

- PDF 转图片 — 每页渲染为高清 PNG/JPG
- PPT 拆分图片 — 每张幻灯片导出为图片序列
- 图片转 PDF — JPG/PNG/WebP 组合合成 PDF
- Word 转 PDF — .docx 本地转换
- Excel 转 PDF — .xlsx 表格渲染输出
- PPT 转 PDF — .pptx 幻灯片无损转换
- PDF 转 Word — 文本提取与基础布局还原
- PDF 转 Excel — 表格结构识别与数据导出
- **HTML 转 PDF** — 粘贴代码或上传文件，实时预览后导出
- **EPUB 转 PDF / Word** — 电子书章节解析，重新排版导出

### PDF 核心工具

- PDF 压缩 — 智能压缩，可选低/中/高质量
- PDF 合并 — 多文件拖拽排序合并
- PDF 拆分 — 按页码范围精确拆分
- **全格式文件水印** — PDF/图片/Office 文档添加文本或图案水印，快速预设 + 实时预览
- **智能隐私脱敏** — 自动识别 + 手动框选涂抹敏感信息，物理级抹除
- **内嵌图片提取** — 从 Word/PPT/PDF 闪电解包所有高清原图
- **电子签章 / 手写签名** — 本地印章库 + 压感手写签名
- **Markdown 转 PDF** — 实时排版编辑器，4 套高美感主题，一键导出 PDF/长图
- **OCR 文字识别** — OCR 引擎高精度提取文字，支持纯文本/保留格式两种输出模式，中英混合识别（需 OCR 后端服务）

### 安全与防御

- PDF 加密 — **AES-256-GCM 真实加密**，PBKDF2 密钥派生
- PDF 权限控制 — 细粒度锁定打印/复制/修改
- PDF 解密 — 已知密码一键移除安全限制
- PDF 数字签名 — X.509 证书本地签名

### 其他

- 深色/浅色主题切换 — 持久化 localStorage
- 中英文界面切换
- 留言反馈 — 内置留言板，支持回复/删除

## 技术栈


| 类别     | 技术                                          |
| ---------- | ----------------------------------------------- |
| 前端框架 | 原生 HTML + JavaScript + Tailwind CSS         |
| PDF 处理 | PDF-Lib, PDF.js                               |
| 文档处理 | JSZip, SheetJS (XLSX), marked.js, html2canvas |
| 加密     | Web Crypto API (AES-256-GCM + PBKDF2)         |
| 后端     | Node.js (留言), Python Flask (OCR)            |
| 部署     | Docker + Docker Compose                       |

## 快速开始

### 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/dongying-AI/LitePDF.git
cd LitePDF

# 2. 启动前端
python -m http.server 8088
# 访问 http://localhost:8088

# 3. 启动留言后端（可选）
node server.js

# 4. 启动 OCR 后端（可选）
pip install paddlepaddle==2.6.2 paddleocr==2.8.1 flask flask-cors pillow numpy
python ocr_server.py
```

### Docker 一键部署

```bash
# 启动全部服务（前端 + 留言 + OCR）
docker compose up -d

# 首次构建或依赖变更后需重建
docker compose build --no-cache
docker compose up -d
```

服务端口：


| 服务     | 端口 | 说明                   |
| ---------- | ------ | ------------------------ |
| 前端     | 8088 | Nginx 静态页面         |
| 留言 API | 3000 | Node.js 后端           |
| OCR API  | 5000 | OCR 后端               |

## 隐私说明

- 所有文件处理均在浏览器本地完成，不上传任何服务器
- 加密使用 Web Crypto API，密钥不离开本地
- 留言功能数据保存在本地服务器
- OCR 功能通过本地后端服务完成

## License

MIT License
