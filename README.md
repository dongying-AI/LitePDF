# LitePDF - 本地文档处理工具箱

一款纯前端实现的本地文档处理工具箱，支持 PDF、Word、Excel、PPT、图片等多种格式的转换、压缩、合并、拆分、水印等功能。所有处理均在浏览器本地完成，无需上传文件到服务器。

## 功能特性

### 格式互转

- PDF 转图片
- PPT 拆分（导出每页为图片）
- 图片转 PDF
- Word 转 PDF
- Excel 转 PDF
- PPT 转 PDF
- PDF 转 Word
- PDF 转 Excel

### PDF 核心工具

- PDF 压缩
- PDF 合并
- PDF 拆分
- **全格式文件水印** - 支持 PDF、图片、Word、Excel、PPT 添加水印
- **智能隐私脱敏** - 自动识别/手动涂抹敏感信息
- **内嵌图片提取** - 从文档中提取所有嵌入图片
- **电子签章/手写签名** - 本地印章库 + 手写签名

### 安全与防御

- PDF 加密
- PDF 权限控制
- PDF 解密
- PDF 数字签名

### 留言反馈

内置留言板功能，支持发布留言、回复、删除。数据通过后端 API 保存到服务器。

## 技术栈

- **前端**: 原生 HTML + JavaScript + Tailwind CSS
- **PDF 处理**: PDF-Lib, PDF.js
- **文档处理**: JSZip, SheetJS (XLSX)
- **后端**: Node.js (留言功能)

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/LitePDF.git
cd LitePDF
```

### 2. 启动前端服务

```bash
# 使用 Python
python -m http.server 8088

# 或使用 Node.js
npx http-server -p 8088
```

访问 http://localhost:8088

### 3. 启动后端服务（可选，用于留言功能）

```bash
node server.js
```

后端服务运行在 http://localhost:3000

## 使用说明

1. 打开网页后，从左侧选择需要的工具
2. 上传文件（支持拖拽）
3. 配置参数（如有）
4. 点击执行，处理完成后自动下载

## 隐私说明

- 所有文件处理均在浏览器本地完成
- 文件不会被上传到任何服务器
- 留言功能需要连接后端服务

## License

MIT License
