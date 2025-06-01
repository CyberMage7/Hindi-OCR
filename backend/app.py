from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import logging
import time
from werkzeug.utils import secure_filename

from ocr.hindi_ocr import perform_hindi_ocr
from qa.question_answer import qa_all

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",  # Local development
            "https://*.vercel.app",   # Vercel deployments
            os.getenv("FRONTEND_URL", "")  # Custom frontend URL
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload to 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Service is healthy'})

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    logger.info("OCR API endpoint called")
    start_time = time.time()
    
    if 'image' not in request.files:
        logger.warning("No image file in request")
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        logger.warning("Empty filename in request")
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            logger.info("Starting OCR process on uploaded file")
            
            # Perform OCR directly on the file object without saving
            extracted_text = perform_hindi_ocr(file)
            logger.info(f"OCR completed in {time.time() - start_time:.2f} seconds")
            
            if not extracted_text or extracted_text.isspace():
                logger.warning("No text detected in the image")
                return jsonify({
                    'text': 'No text detected. Please try a clearer image with visible Hindi text.',
                    'qa_pairs': [
                        {
                            'question': 'क्यों कोई पाठ नहीं मिला?',
                            'answer': 'छवि में कोई पाठ नहीं मिला या OCR पहचान विफल रही। कृपया स्पष्ट हिंदी पाठ वाली एक अलग छवि का प्रयास करें।'
                        }
                    ]
                })
            
            # Check for common OCR errors - all zeros
            if all(c == '0' for c in extracted_text):
                logger.warning("OCR returned all zeros - likely a recognition problem")
                return jsonify({
                    'text': 'OCR पहचान में समस्या। कृपया अधिक स्पष्ट छवि का प्रयास करें।',
                    'qa_pairs': [
                        {
                            'question': 'OCR परिणाम क्यों सही नहीं है?',
                            'answer': 'छवि सही से पहचानी नहीं गई। कृपया एक स्पष्ट छवि का प्रयास करें या सुनिश्चित करें कि छवि में हिंदी पाठ है।'
                        }
                    ]
                })
            
            # Generate QA pairs from the extracted text
            logger.info("Starting QA generation")
            qa_start_time = time.time()
            qa_pairs = qa_all(extracted_text)
            logger.info(f"QA generation completed in {time.time() - qa_start_time:.2f} seconds")
            
            # Calculate total processing time
            total_time = time.time() - start_time
            logger.info(f"Total request processed in {total_time:.2f} seconds")
            
            return jsonify({
                'text': extracted_text,
                'qa_pairs': qa_pairs,
                'processing_time': f"{total_time:.2f} seconds"
            })
        
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'An error occurred during processing.',
                'message': str(e)
            }), 500
    
    logger.warning(f"Invalid file format: {file.filename}")
    return jsonify({'error': 'Invalid file format. Allowed formats are: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400

if __name__ == '__main__':
    logger.info("Starting Hindi OCR and QA Generator service")
    app.run(debug=True, host='0.0.0.0', port=5000)
