# pdf_processor.py
import pdfplumber
from pdf2image import convert_from_path
from pytesseract import image_to_string
import os

def validate_pdf(pdf_path):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("The provided file is not a valid PDF.")

def extract_text_from_pdf(pdf_path):
    validate_pdf(pdf_path)
    
    try:
        # Attempt to read text using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages)
        
        # If text is empty, fallback to OCR
        if not text.strip():
            print("No text found in PDF. Falling back to OCR.")
            images = convert_from_path(pdf_path, dpi=300)
            text = ''.join(image_to_string(image) for image in images)
        
        if not text.strip():
            raise ValueError("The PDF does not contain readable text or images.")
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise
