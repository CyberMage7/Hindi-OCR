import os
import sys
import logging
import numpy as np
import cv2
from PIL import Image
import pytesseract
import torch
import easyocr
import time
import tempfile
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize EasyOCR reader (only once)
reader = None

def get_easyocr_reader():
    """Initialize EasyOCR reader with Hindi language"""
    global reader
    if reader is None:
        try:
            logger.info("Initializing EasyOCR with Hindi language support")
            reader = easyocr.Reader(['hi', 'en'], gpu=torch.cuda.is_available())
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            reader = None
    return reader

def check_tesseract_hindi():
    """Check if Tesseract has Hindi language support"""
    try:
        # Check for Hindi language data in common locations
        hindi_data_paths = [
            '/usr/share/tesseract-ocr/4.00/tessdata/hin.traineddata',
            '/usr/share/tesseract-ocr/tessdata/hin.traineddata',
            'C:\\Program Files\\Tesseract-OCR\\tessdata\\hin.traineddata',
            str(Path.home() / 'tessdata' / 'hin.traineddata')
        ]
        
        for path in hindi_data_paths:
            if os.path.exists(path):
                logger.info(f"Found Hindi Tesseract data at: {path}")
                return True
        
        # If not found in common locations, try to query tesseract for available languages
        try:
            result = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True, check=False)
            available_langs = result.stdout.split('\n')
            if 'hin' in available_langs:
                logger.info("Hindi language available in Tesseract")
                return True
        except:
            pass
            
        logger.warning("Hindi language data not found for Tesseract")
        return False
    except Exception as e:
        logger.error(f"Error checking Tesseract Hindi support: {str(e)}")
        return False

def enhance_image_for_hindi_ocr(image):
    """Apply special enhancements for Hindi text recognition"""
    try:
        # Convert to numpy array if PIL image
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image.copy()
        
        # Convert to grayscale if color
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np.copy()
        
        # Noise removal and smoothing
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding - better for varying lighting conditions
        # For Hindi text, we want to preserve thin connecting lines between characters
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Invert if needed (white text on black background)
        if np.mean(thresh) < 127:
            thresh = cv2.bitwise_not(thresh)
        
        # Dilate to make text more prominent
        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        # Create enhanced color version for neural models
        enhanced_color = cv2.cvtColor(dilated, cv2.COLOR_GRAY2RGB)
        
        # Return multiple versions for different OCR methods
        return {
            'original': image_np,
            'grayscale': gray, 
            'threshold': thresh,
            'enhanced': dilated,
            'color_enhanced': enhanced_color,
            'pil_enhanced': Image.fromarray(dilated)
        }
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        if isinstance(image, Image.Image):
            return {'original': np.array(image), 'pil_enhanced': image}
        return {'original': image, 'pil_enhanced': Image.fromarray(image)}

def use_easyocr(image_dict):
    """Use EasyOCR specialized for Hindi text"""
    try:
        reader = get_easyocr_reader()
        if reader is None:
            logger.warning("EasyOCR not available")
            return None
            
        logger.info("Performing OCR with EasyOCR")
        start_time = time.time()
        
        # Use the original image for EasyOCR as it has its own preprocessing
        original_image = image_dict.get('original')
        if original_image is None:
            return None
        
        # EasyOCR settings optimized for Hindi
        results = reader.readtext(
            original_image,
            detail=0,  # Just get the text
            paragraph=True, 
            decoder='greedy',
            beamWidth=5,
            batch_size=1,
            contrast_ths=0.1, 
            adjust_contrast=0.5,
            text_threshold=0.7,
            link_threshold=0.4,
            add_margin=0.1,
        )
        
        text = '\n'.join(results)
        logger.info(f"EasyOCR completed in {time.time() - start_time:.2f} seconds")
        logger.info(f"EasyOCR result: {text[:100]}...")
        
        # Check if the result is mostly digits or empty
        if not text or all(c.isdigit() or c.isspace() for c in text):
            logger.warning("EasyOCR returned only digits or spaces")
            return None
            
        return text
    except Exception as e:
        logger.error(f"Error using EasyOCR: {str(e)}")
        return None

def use_tesseract_for_hindi(image_dict):
    """Use Tesseract OCR configured for Hindi"""
    try:
        has_hindi = check_tesseract_hindi()
        
        enhanced_image = image_dict.get('enhanced', image_dict.get('original'))
        if enhanced_image is None:
            return None
            
        logger.info("Performing OCR with Tesseract")
        start_time = time.time()
        
        # Configure Tesseract for Hindi
        if has_hindi:
            custom_config = r'--oem 3 --psm 6 -l hin+eng'
        else:
            custom_config = r'--oem 3 --psm 6'  # Use default language
            
        # Try with different page segmentation modes if needed
        psm_modes = [6, 4, 3, 11]
        
        for psm in psm_modes:
            config = f'--oem 3 --psm {psm}' + (' -l hin+eng' if has_hindi else '')
            text = pytesseract.image_to_string(enhanced_image, config=config)
            
            # Clean the text
            text = text.strip()
            
            # Check if the result is meaningful
            if text and not all(c.isdigit() or c.isspace() for c in text):
                logger.info(f"Tesseract (PSM {psm}) completed in {time.time() - start_time:.2f} seconds")
                logger.info(f"Tesseract result: {text[:100]}...")
                return text
        
        # If all PSM modes failed, try one more time with the original image
        text = pytesseract.image_to_string(
            image_dict.get('original'), 
            config=r'--oem 3 --psm 6' + (' -l hin+eng' if has_hindi else '')
        )
        
        logger.info(f"Tesseract (final attempt) completed in {time.time() - start_time:.2f} seconds")
        return text.strip()
    except Exception as e:
        logger.error(f"Error using Tesseract: {str(e)}")
        return None

def perform_hindi_ocr(image_input):
    """Main function to perform Hindi OCR using multiple methods
    
    Args:
        image_input: Can be either a file path (string) or a file object (from Flask upload)
    """
    logger.info(f"Starting OCR on image input: {type(image_input)}")
    
    try:
        # Handle file object vs file path
        if hasattr(image_input, 'read'):
            # It's a file object (from Flask upload)
            logger.info("Processing file object")
            
            # Reset file pointer and read image data
            image_input.seek(0)
            image_data = image_input.read()
            
            # Convert file data to OpenCV image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        else:
            # It's a file path
            logger.info(f"Processing file path: {image_input}")
            
            # Read the image from file path
            image = cv2.imread(image_input)
        
        if image is None:
            logger.error("Failed to read/decode image")
            return "Error: Could not read the image file."
        
        # Enhance the image for Hindi OCR
        image_versions = enhance_image_for_hindi_ocr(image)
        
        # Try EasyOCR (specialized for Hindi)
        easyocr_text = use_easyocr(image_versions)
        if easyocr_text and len(easyocr_text) > 5 and not all(c.isdigit() or c.isspace() for c in easyocr_text):
            logger.info("Successfully extracted text using EasyOCR")
            return easyocr_text
        
        # Try Tesseract
        tesseract_text = use_tesseract_for_hindi(image_versions)
        if tesseract_text and len(tesseract_text) > 5 and not all(c.isdigit() or c.isspace() for c in tesseract_text):
            logger.info("Successfully extracted text using Tesseract")
            return tesseract_text
        
        # If all methods failed or returned only digits
        if easyocr_text:
            return easyocr_text
        if tesseract_text:
            return tesseract_text
            
        logger.warning("All OCR methods failed to extract meaningful Hindi text")
        return "OCR पहचान में समस्या। कृपया अधिक स्पष्ट छवि का प्रयास करें।"
        
    except Exception as e:
        logger.error(f"Error in OCR process: {str(e)}", exc_info=True)
        return f"Error processing image: {str(e)}"
