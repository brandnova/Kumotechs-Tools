# media_toolkit/forms.py
from django import forms

class ImageUploadForm(forms.Form):
    """Form for image upload and processing"""
    file = forms.ImageField(label='Select Image')
    
    # Format conversion
    FORMAT_CHOICES = [
        ('', 'Keep Original'),
        ('JPEG', 'Convert to JPG'),
        ('PNG', 'Convert to PNG'),
        ('WEBP', 'Convert to WEBP'),
        ('GIF', 'Convert to GIF'),
    ]
    convert_format = forms.ChoiceField(choices=FORMAT_CHOICES, required=False, 
                                       label='Convert Format')
    
    # Compression
    compress = forms.BooleanField(required=False, label='Compress Image')
    compression_quality = forms.IntegerField(
        min_value=1, max_value=100, initial=85, required=False,
        label='Compression Quality (1-100, lower = smaller file)'
    )
    
    # OCR
    perform_ocr = forms.BooleanField(required=False, label='Extract Text (OCR)')

class PDFUploadForm(forms.Form):
    """Form for PDF upload and processing"""
    file = forms.FileField(label='Select PDF')
    compress = forms.BooleanField(required=False, initial=True, 
                                 label='Compress PDF')