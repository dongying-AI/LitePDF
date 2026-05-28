"""
PaddleOCR-VL 后端服务
LitePDF OCR 功能的 Python 后端，使用 PaddleOCR 进行文字识别。

安装依赖：
    pip install paddlepaddle paddleocr flask flask-cors pillow numpy

启动服务：
    python ocr_server.py

API：
    POST /ocr
    Body: { "image": "data:image/png;base64,...", "lang": "ch" }
    Response: { "text": "识别结果文本" }
"""

import base64
import io
import os
import sys
import threading

# PaddlePaddle 2.6 禁用 OneDNN，避免连续推理时的 primitive 执行错误
os.environ['FLAGS_use_mkldnn'] = '0'

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

# 延迟初始化，避免首次启动过慢
_ocr = None
_ocr_lock = threading.Lock()

def get_ocr(lang='ch', force_reinit=False):
    global _ocr
    if _ocr is None or force_reinit:
        try:
            from paddleocr import PaddleOCR
            lang_map = {
                'ch': 'ch',
                'eng': 'en',
                'ch_en': 'ch'
            }
            mapped_lang = lang_map.get(lang, 'ch')
            _ocr = PaddleOCR(lang=mapped_lang, ocr_version='PP-OCRv4')
            print(f"[OCR] PaddleOCR initialized, lang={mapped_lang}")
        except ImportError:
            print("[OCR] ERROR: paddleocr not installed. Run: pip install paddlepaddle paddleocr")
            sys.exit(1)
    return _ocr


@app.route('/ocr', methods=['POST'])
def do_ocr():
    data = request.get_json(force=True)
    img_b64 = data.get('image', '')
    lang = data.get('lang', 'ch')

    if not img_b64:
        return jsonify({'error': 'No image provided'}), 400

    # Decode base64 image
    if ',' in img_b64:
        img_b64 = img_b64.split(',', 1)[1]
    img_bytes = base64.b64decode(img_b64)

    try:
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_np = np.array(img)
    except Exception as e:
        return jsonify({'error': f'Image decode failed: {str(e)}'}), 400

    # Run OCR with thread lock (PaddlePaddle C++ backend is not thread-safe)
    h, w = img_np.shape[:2]
    fmt = data.get('format', 'plain')
    print(f"[OCR] Received image: {w}x{h}, lang={lang}, format={fmt}, size={len(img_bytes)} bytes")

    with _ocr_lock:
        ocr = get_ocr(lang)
        try:
            result = ocr.ocr(img_np)
        except Exception as e:
            err_msg = str(e)
            print(f"[OCR] PaddleOCR error: {type(e).__name__}: {err_msg}")
            # 自动重试：OneDNN primitive 错误时重新初始化引擎
            if 'primitive' in err_msg.lower() or 'could not execute' in err_msg.lower():
                print("[OCR] Auto-retrying with fresh OCR engine...")
                global _ocr
                _ocr = None
                try:
                    ocr = get_ocr(lang, force_reinit=True)
                    result = ocr.ocr(img_np)
                    print("[OCR] Retry succeeded")
                except Exception as e2:
                    print(f"[OCR] Retry failed: {type(e2).__name__}: {e2}")
                    return jsonify({'error': f'OCR engine error: {str(e2)}'}), 500
            else:
                return jsonify({'error': f'OCR engine error: {err_msg}'}), 500

        # Extract text based on format
        texts = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                texts.append(text)

        output_text = '\n'.join(texts)
        if fmt == 'structured':
            output_text = _structured_text(result[0])

    return jsonify({
        'text': output_text,
        'lines': len(texts)
    })


def _structured_text(ocr_result):
    """根据文本框坐标恢复行结构和段落。
    ocr_result: list of [[box], (text, conf)]
    box: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    """
    if not ocr_result:
        return ''

    # 收集每个文本框的中心坐标和文本
    boxes = []
    for item in ocr_result:
        box = item[0]  # 4个角点
        text = item[1][0]
        # 中心点
        cx = sum(p[0] for p in box) / 4.0
        cy = sum(p[1] for p in box) / 4.0
        # 行高（上下边的平均高度差）
        top_y = min(p[1] for p in box)
        bottom_y = max(p[1] for p in box)
        height = bottom_y - top_y
        boxes.append({'text': text, 'cx': cx, 'cy': cy, 'height': height, 'top': top_y, 'bottom': bottom_y})

    # 按中心 Y 坐标排序
    boxes.sort(key=lambda b: b['cy'])

    # 聚类：相近 Y 坐标的归为同一行
    rows = []
    current_row = [boxes[0]]
    for b in boxes[1:]:
        # 如果当前文本框与上一行中心 Y 的差值小于平均行高的一半，认为是同一行
        prev = current_row[-1]
        avg_h = (b['height'] + prev['height']) / 2
        if abs(b['cy'] - prev['cy']) < avg_h * 0.6:
            current_row.append(b)
        else:
            rows.append(current_row)
            current_row = [b]
    rows.append(current_row)

    # 每行内按 X 坐标排序，从左到右
    lines = []
    for row in rows:
        row.sort(key=lambda b: b['cx'])
        line_text = ''.join(b['text'] for b in row)
        lines.append(line_text)

    # 段落检测：行间距大于 1.5 倍平均行高时插入空行
    if len(lines) <= 1:
        return '\n'.join(lines)

    # 计算相邻行的间距
    gaps = []
    for i in range(1, len(rows)):
        prev_bottom = max(b['bottom'] for b in rows[i-1])
        curr_top = min(b['top'] for b in rows[i])
        gaps.append(curr_top - prev_bottom)

    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    avg_h = sum(b['height'] for row in rows for b in row) / len(boxes)

    result_lines = [lines[0]]
    for i, gap in enumerate(gaps):
        if gap > avg_h * 1.2:  # 间距较大，认为是段落分隔
            result_lines.append('')
        result_lines.append(lines[i + 1])

    return '\n'.join(result_lines)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("[OCR] Starting PaddleOCR server on http://127.0.0.1:5000")
    print("[OCR] First request will initialize the model (may take a few seconds)")
    app.run(host='0.0.0.0', port=5000, debug=False)
