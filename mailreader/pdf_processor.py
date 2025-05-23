# pdf_processor.py - Modified to work without pytesseract
import os
import logging

# Global flag to track if OCR is available
ocr_available = False

# Try to import pdfplumber - essential
try:
    import pdfplumber
    pdfplumber_available = True
except ImportError:
    pdfplumber_available = False
    logging.error("pdfplumber not available - PDF text extraction will not work")

# Try to import pdf2image and pytesseract - optional for OCR
try:
    from pdf2image import convert_from_path
    import pytesseract
    from pytesseract import image_to_string
    ocr_available = True
    logging.info("OCR capabilities available")
except ImportError:
    ocr_available = False
    logging.warning("pytesseract or pdf2image not available - OCR capabilities disabled")

def validate_pdf(pdf_path):
    """Validate if a file is a valid PDF"""
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("The provided file is not a valid PDF.")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file, with fallback if OCR is not available"""
    validate_pdf(pdf_path)
    
    if not pdfplumber_available:
        raise RuntimeError("PDF text extraction is not available because pdfplumber is missing.")
    
    try:
        # Attempt to read text using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages)
        
        # If text is empty and OCR is available, fall back to OCR
        if not text.strip() and ocr_available:
            logging.info("No text found in PDF. Falling back to OCR.")
            try:
                images = convert_from_path(pdf_path, dpi=300)
                text = ''.join(image_to_string(image) for image in images)
            except Exception as ocr_error:
                logging.error(f"OCR failed: {ocr_error}")
                text = "(OCR failed - could not extract text from images)"
        
        # If OCR is not available and no text was found
        if not text.strip() and not ocr_available:
            logging.warning("No text found in PDF and OCR is not available.")
            text = "(This PDF appears to contain images or scanned text. OCR capabilities are not available to extract text from images.)"
        
        if not text.strip():
            text = "(No readable text found in this PDF)"
        
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {e}")