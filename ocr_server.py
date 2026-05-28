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
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

# 延迟初始化，避免首次启动过慢
_ocr = None

def get_ocr(lang='ch'):
    global _ocr
    if _ocr is None:
        try:
            from paddleocr import PaddleOCR
            lang_map = {
                'ch': 'ch',
                'eng': 'en',
                'ch_en': 'ch'
            }
            mapped_lang = lang_map.get(lang, 'ch')
            _ocr = PaddleOCR(lang=mapped_lang)
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

    # Run OCR (with size limit to avoid crashes)
    h, w = img_np.shape[:2]
    print(f"[OCR] Received image: {w}x{h}, lang={lang}, size={len(img_bytes)} bytes")
    if w < 4 or h < 4:
        return jsonify({'error': 'Image too small'}), 400
    if max(w, h) > 4096:
        # Downscale large images
        scale = 4096 / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img_np = np.array(img)
        print(f"[OCR] Downscaled to {new_w}x{new_h}")

    ocr = get_ocr(lang)
    try:
        result = ocr.ocr(img_np)
    except Exception as e:
        print(f"[OCR] PaddleOCR error: {type(e).__name__}: {e}")
        return jsonify({'error': f'OCR engine error: {str(e)}'}), 500

    # Extract text lines
    texts = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            texts.append(text)

    return jsonify({
        'text': '\n'.join(texts),
        'lines': len(texts)
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("[OCR] Starting PaddleOCR server on http://127.0.0.1:5000")
    print("[OCR] First request will initialize the model (may take a few seconds)")
    app.run(host='0.0.0.0', port=5000, debug=False)
