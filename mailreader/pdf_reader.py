from pdf2image import convert_from_path
from pytesseract import image_to_string
from pdfplumber import open as pdf_open
import os
import camelot

def extract_text_from_pdf(file_path):
    try:
        # Extract text using pdfplumber for non-tabular content
        with pdfplumber.open(file_path) as pdf:
            text = ''.join(page.extract_text() for page in pdf.pages)
        
        # Extract tables using Camelot
        tables = camelot.read_pdf(file_path, pages='all')
        for table in tables:
            text += "\n" + table.df.to_string()  # Add table data as text

        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {e}")


def validate_pdf(pdf_path):
    """Validates the PDF file to ensure it exists and is in the correct format."""
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("The provided file is not a valid PDF.")

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file. Falls back to OCR if the PDF contains images instead of text.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        str: The extracted text.
    """
    validate_pdf(pdf_path)
    
    try:
        # Attempt to read text using pdfplumber
        with pdf_open(pdf_path) as pdf:
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
