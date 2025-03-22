# media_toolkit/utils.py
import os
import uuid
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO

def ensure_temp_dir():
    """Ensure the temporary directory exists"""
    os.makedirs(settings.TEMP_ROOT, exist_ok=True)
    
def get_temp_path(filename):
    """Generate a temporary file path"""
    ensure_temp_dir()
    filename = os.path.basename(filename)
    return os.path.join(settings.TEMP_ROOT, filename)

def convert_image_format(input_path, output_format='JPEG'):
    """Convert image to the specified format"""
    output_formats = {
        'JPEG': 'jpg',
        'PNG': 'png',
        'WEBP': 'webp',
        'GIF': 'gif',
    }
    
    if output_format not in output_formats:
        raise ValueError(f"Unsupported format: {output_format}")
    
    # Generate output filename
    file_name = f"{uuid.uuid4()}.{output_formats[output_format]}"
    output_path = get_temp_path(file_name)
    
    # Convert image
    img = Image.open(input_path)
    rgb_img = img.convert('RGB') if output_format == 'JPEG' and img.mode == 'RGBA' else img
    rgb_img.save(output_path, format=output_format)
    
    return output_path, file_name

def compress_image(input_path, quality=85):
    """Compress image while maintaining reasonable quality"""
    img = Image.open(input_path)
    
    # Get original file extension
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        ext = '.jpg'  # Default to jpg if unsupported
    
    # Generate output filename
    file_name = f"{uuid.uuid4()}_compressed{ext}"
    output_path = get_temp_path(file_name)
    
    # Convert to RGB if needed
    if img.mode == 'RGBA' and ext in ['.jpg', '.jpeg']:
        img = img.convert('RGB')
    
    # Compress and save
    img.save(output_path, optimize=True, quality=quality)
    
    return output_path, file_name

def compress_pdf(input_path):
    """Compress PDF using PyMuPDF"""
    # Generate output filename
    file_name = f"{uuid.uuid4()}_compressed.pdf"
    output_path = get_temp_path(file_name)
    
    # Open the PDF with PyMuPDF
    doc = fitz.open(input_path)
    
    # Set parameters for optimization
    params = {
        "garbage": 4,  # Clean up the PDF structure
        "clean": 1,    # Clean up unnecessary elements
        "deflate": 1,  # Compress streams
    }
    
    # Save with optimization
    doc.save(output_path, garbage=params["garbage"], clean=params["clean"], 
             deflate=params["deflate"])
    doc.close()
    
    return output_path, file_name

def extract_text_from_image(input_path):
    """Extract text from image using OCR"""
    img = Image.open(input_path)
    
    # Use pytesseract to extract text
    text = pytesseract.image_to_string(img)
    
    # Generate output text file
    file_name = f"{uuid.uuid4()}_extracted_text.txt"
    output_path = get_temp_path(file_name)
    
    # Save extracted text to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return output_path, file_name, text