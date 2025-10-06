import pdfplumber
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(pdf_path):
    """Extracts all text from a PDF, using OCR if a page is image-based."""
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                all_text += text + "\n"
            else:
                # Handle scanned/image-based PDF page with OCR
                image = page.to_image(resolution=300).original
                pil_image = Image.open(io.BytesIO(image.convert("RGB").tobytes()))
                text_ocr = pytesseract.image_to_string(pil_image)
                all_text += text_ocr + "\n"
    return all_text.strip()

import os

def get_resume_text(resume_path):
    # Detect filetype from extension
    file_ext = os.path.splitext(resume_path)[1].lower()
    if file_ext == ".pdf":
        resume_text = extract_text_from_pdf(resume_path)   # your existing PDF function
    elif file_ext == ".txt":
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
    else:
        raise ValueError("Unsupported resume file format! Please provide PDF or TXT.")
    return resume_text
