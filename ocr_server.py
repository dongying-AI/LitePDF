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
            _ocr = PaddleOCR(
                lang=mapped_lang,
                use_gpu=False
            )
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

    # Run OCR
    ocr = get_ocr(lang)
    result = ocr.ocr(img_np, cls=True)

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
    app.run(host='127.0.0.1', port=5000, debug=False)
