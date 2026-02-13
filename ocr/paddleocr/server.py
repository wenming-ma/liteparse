from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np

app = Flask(__name__)
ocr = None
current_language = None

# Language mapping from ISO codes to PaddleOCR codes
LANGUAGE_MAP = {
    'en': 'en',
    'zh': 'ch',
    'zh-cn': 'ch',
    'zh-hans': 'ch',
    'zh-tw': 'chinese_cht',
    'zh-hant': 'chinese_cht',
    'ja': 'japan',
    'ko': 'korean',
    'fr': 'french',
    'de': 'german',
    'es': 'spanish',
    'pt': 'portuguese',
    'ru': 'russian',
    'ar': 'arabic',
    'hi': 'devanagari',
}

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    global ocr, current_language

    # Get language from request
    language = request.form.get('language', 'en').lower()
    paddle_lang = LANGUAGE_MAP.get(language, language)

    # Initialize OCR if needed or language changed
    if ocr is None or current_language != paddle_lang:
        print(f"Initializing PaddleOCR for language: {paddle_lang}")
        # PaddleOCR 3.x parameters
        ocr = PaddleOCR(
            lang=paddle_lang,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=True,
        )
        current_language = paddle_lang

    # Read image
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    # Load image
    image_data = file.read()
    image = Image.open(io.BytesIO(image_data))

    # Convert to numpy array (RGB)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image_array = np.array(image)

    # Run OCR
    # PaddleOCR 3.x returns: list of result dicts
    # Each result has: res['rec_texts'], res['rec_scores'], res['rec_boxes']
    results = ocr.predict(image_array)

    # Debug: print result structure
    print(f"Results type: {type(results)}")
    if results:
        print(f"First result type: {type(results[0])}")
        if hasattr(results[0], '__dict__'):
            print(f"First result attrs: {dir(results[0])}")
        if isinstance(results[0], dict):
            print(f"First result keys: {results[0].keys()}")

    # Format results according to LiteParse OCR API spec
    # Convert to: { text, bbox: [x1, y1, x2, y2], confidence }
    formatted = []

    if results and len(results) > 0:
        # Get the first result
        result = results[0]

        res_data = result.get('res', result) if isinstance(result, dict) else result
        print(f"res_data type: {type(res_data)}, keys/attrs: {res_data.keys() if isinstance(res_data, dict) else dir(res_data)}")

        # Extract texts, scores, and boxes from the result
        if isinstance(res_data, dict):
            texts = res_data.get('rec_texts', [])
            scores = res_data.get('rec_scores', [])
            boxes = res_data.get('rec_boxes', [])
        else:
            # Fallback for result object with attributes
            texts = getattr(res_data, 'rec_texts', []) or []
            scores = getattr(res_data, 'rec_scores', []) or []
            boxes = getattr(res_data, 'rec_boxes', []) or []

        # Convert numpy arrays to lists if needed
        if hasattr(texts, 'tolist'):
            texts = texts.tolist()
        if hasattr(scores, 'tolist'):
            scores = scores.tolist()
        if hasattr(boxes, 'tolist'):
            boxes = boxes.tolist()

        # Combine them - they should be parallel arrays
        for i in range(len(texts)):
            text = texts[i]
            confidence = float(scores[i]) if i < len(scores) else 0.0

            # Get bounding box coordinates
            # rec_boxes format is typically [x_min, y_min, x_max, y_max]
            if i < len(boxes):
                box = boxes[i]
                # Convert to list and ensure 4 coordinates
                if hasattr(box, 'tolist'):
                    bbox = box.tolist()
                else:
                    bbox = list(box)
            else:
                bbox = [0, 0, 0, 0]

            formatted.append({
                'text': text,
                'bbox': bbox,
                'confidence': confidence
            })

    return jsonify({
        'results': formatted
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8829)
