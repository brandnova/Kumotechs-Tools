import qrcode # type: ignore
from io import BytesIO
import base64
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os

def generate_qr_code(data, logo_path=None, size=10, color="black", bg_color="white", text=None, convert_bw=False):
    """
    Generate a QR code for the given data with optional logo and text
    Returns the QR code as a base64 encoded string
    
    Parameters:
    - data: The URL or text to encode in the QR code
    - logo_path: Optional path to a logo image to place in the center
    - size: Box size of QR code (default: 10)
    - color: Fill color of QR code (default: black)
    - bg_color: Background color of QR code (default: white)
    - text: Optional text to add below the QR code
    - convert_bw: Whether to convert the logo to black and white
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_H,  # Use high error correction for logo
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=color, back_color=bg_color)
    img = img.convert('RGBA')
    
    # If logo is provided, add it to the center of the QR code
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            
            # Convert logo to black and white if requested
            if convert_bw:
                logo = logo.convert('L')  # Convert to grayscale
                # Convert to pure black and white (1-bit)
                threshold = 128
                logo = logo.point(lambda p: 255 if p > threshold else 0)
                # Convert back to RGBA
                logo = logo.convert('RGBA')
            
            # Calculate logo size (max 30% of QR code)
            logo_max_size = img.size[0] // 3
            logo_width, logo_height = logo.size
            
            # Resize logo if needed
            if logo_width > logo_max_size or logo_height > logo_max_size:
                if logo_width > logo_height:
                    new_width = logo_max_size
                    new_height = int(logo_height * (logo_max_size / logo_width))
                else:
                    new_height = logo_max_size
                    new_width = int(logo_width * (logo_max_size / logo_height))
                logo = logo.resize((new_width, new_height))
            
            # Calculate position to center the logo
            pos_x = (img.size[0] - logo.size[0]) // 2
            pos_y = (img.size[1] - logo.size[1]) // 2
            
            # Create a white background for the logo if not in B&W mode
            if not convert_bw:
                logo_bg = Image.new('RGBA', logo.size, (255, 255, 255, 255))
                logo_with_bg = Image.alpha_composite(logo_bg, logo.convert('RGBA'))
                # Paste the logo onto the QR code
                img.paste(logo_with_bg, (pos_x, pos_y), logo_with_bg)
            else:
                # For B&W logos, just paste directly
                img.paste(logo, (pos_x, pos_y), logo)
                
        except Exception as e:
            # If there's an error with the logo, just use the QR code without it
            print(f"Error adding logo to QR code: {e}")
    
    # If text is provided, add it below the QR code
    if text and text.strip():
        # Create a new image with space for the text
        text = text.strip()
        font_size = max(10, img.size[0] // 15)  # Scale font size based on QR code size
        
        try:
            # Try to use a system font
            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'arial.ttf')
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                # Fall back to default font
                font = ImageFont.load_default()
                
            # Calculate text dimensions
            draw = ImageDraw.Draw(img)
            text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (font_size * len(text) * 0.6, font_size * 1.5)
            
            # Create a new image with space for the text
            text_padding = 10
            new_height = img.size[1] + text_height + text_padding * 2
            new_img = Image.new('RGBA', (img.size[0], new_height), bg_color)
            
            # Paste the QR code onto the new image
            new_img.paste(img, (0, 0))
            
            # Add the text
            draw = ImageDraw.Draw(new_img)
            text_x = (img.size[0] - text_width) // 2
            text_y = img.size[1] + text_padding
            
            # Draw the text
            if hasattr(draw, 'textsize'):
                draw.text((text_x, text_y), text, fill=color, font=font)
            else:
                # For newer Pillow versions
                draw.text((text_x, text_y), text, fill=color)
            
            img = new_img
        except Exception as e:
            print(f"Error adding text to QR code: {e}")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # Convert to base64 for embedding in HTML
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def save_qr_code(data, filename, logo_path=None, size=10, color="black", bg_color="white", text=None, convert_bw=False):
    """
    Generate a QR code and save it to a file
    Returns the file path
    
    Parameters:
    - data: The URL or text to encode in the QR code
    - filename: Name of the file to save
    - logo_path: Optional path to a logo image to place in the center
    - size: Box size of QR code (default: 10)
    - color: Fill color of QR code (default: black)
    - bg_color: Background color of QR code (default: white)
    - text: Optional text to add below the QR code
    - convert_bw: Whether to convert the logo to black and white
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_H,  # Use high error correction for logo
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=color, back_color=bg_color)
    img = img.convert('RGBA')
    
    # If logo is provided, add it to the center of the QR code
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            
            # Convert logo to black and white if requested
            if convert_bw:
                logo = logo.convert('L')  # Convert to grayscale
                # Convert to pure black and white (1-bit)
                threshold = 128
                logo = logo.point(lambda p: 255 if p > threshold else 0)
                # Convert back to RGBA
                logo = logo.convert('RGBA')
            
            # Calculate logo size (max 30% of QR code)
            logo_max_size = img.size[0] // 3
            logo_width, logo_height = logo.size
            
            # Resize logo if needed
            if logo_width > logo_max_size or logo_height > logo_max_size:
                if logo_width > logo_height:
                    new_width = logo_max_size
                    new_height = int(logo_height * (logo_max_size / logo_width))
                else:
                    new_height = logo_max_size
                    new_width = int(logo_width * (logo_max_size / logo_height))
                logo = logo.resize((new_width, new_height))
            
            # Calculate position to center the logo
            pos_x = (img.size[0] - logo.size[0]) // 2
            pos_y = (img.size[1] - logo.size[1]) // 2
            
            # Create a white background for the logo if not in B&W mode
            if not convert_bw:
                logo_bg = Image.new('RGBA', logo.size, (255, 255, 255, 255))
                logo_with_bg = Image.alpha_composite(logo_bg, logo.convert('RGBA'))
                # Paste the logo onto the QR code
                img.paste(logo_with_bg, (pos_x, pos_y), logo_with_bg)
            else:
                # For B&W logos, just paste directly
                img.paste(logo, (pos_x, pos_y), logo)
                
        except Exception as e:
            # If there's an error with the logo, just use the QR code without it
            print(f"Error adding logo to QR code: {e}")
    
    # If text is provided, add it below the QR code
    if text and text.strip():
        # Create a new image with space for the text
        text = text.strip()
        font_size = max(10, img.size[0] // 15)  # Scale font size based on QR code size
        
        try:
            # Try to use a system font
            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'arial.ttf')
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                # Fall back to default font
                font = ImageFont.load_default()
                
            # Calculate text dimensions
            draw = ImageDraw.Draw(img)
            text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (font_size * len(text) * 0.6, font_size * 1.5)
            
            # Create a new image with space for the text
            text_padding = 10
            new_height = img.size[1] + text_height + text_padding * 2
            new_img = Image.new('RGBA', (img.size[0], new_height), bg_color)
            
            # Paste the QR code onto the new image
            new_img.paste(img, (0, 0))
            
            # Add the text
            draw = ImageDraw.Draw(new_img)
            text_x = (img.size[0] - text_width) // 2
            text_y = img.size[1] + text_padding
            
            # Draw the text
            if hasattr(draw, 'textsize'):
                draw.text((text_x, text_y), text, fill=color, font=font)
            else:
                # For newer Pillow versions
                draw.text((text_x, text_y), text, fill=color)
            
            img = new_img
        except Exception as e:
            print(f"Error adding text to QR code: {e}")
    
    # Create directory if it doesn't exist
    media_root = getattr(settings, 'MEDIA_ROOT', 'media')
    qr_dir = os.path.join(media_root, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Create fonts directory if it doesn't exist
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Save the image
    file_path = os.path.join(qr_dir, filename)
    img.save(file_path)
    
    # Return the relative path for storage in the database
    return os.path.join('qrcodes', filename)

def process_logo(logo_file, output_filename):
    """
    Process a logo for use in QR codes
    - Resize to appropriate dimensions
    - Convert to RGBA format
    
    Returns the path to the processed logo
    """
    try:
        # Create directory if it doesn't exist
        media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        logo_dir = os.path.join(media_root, 'logos')
        os.makedirs(logo_dir, exist_ok=True)
        
        # Open and process the logo
        logo = Image.open(logo_file)
        
        # Resize to a reasonable size for QR codes (max 150x150)
        max_size = 150
        if logo.width > max_size or logo.height > max_size:
            if logo.width > logo.height:
                new_width = max_size
                new_height = int(logo.height * (max_size / logo.width))
            else:
                new_height = max_size
                new_width = int(logo.width * (max_size / logo.height))
            logo = logo.resize((new_width, new_height))
        
        # Ensure it's in RGBA format
        logo = logo.convert('RGBA')
        
        # Save the processed logo
        output_path = os.path.join(logo_dir, output_filename)
        logo.save(output_path)
        
        return os.path.join('logos', output_filename)
    except Exception as e:
        print(f"Error processing logo: {e}")
        return None

