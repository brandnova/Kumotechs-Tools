# media_toolkit/models.py
import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def get_temp_file_path(instance, filename):
    """Generate a unique path for uploaded files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'temp/{filename}'

class ProcessedFile(models.Model):
    """Model to track processed files"""
    PROCESSING_TYPE_CHOICES = [
        ('format_conversion', 'Format Conversion'),
        ('image_compression', 'Image Compression'),
        ('pdf_compression', 'PDF Compression'),
        ('ocr', 'OCR Text Extraction'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.FileField(upload_to=get_temp_file_path)
    processed_file = models.FileField(upload_to=get_temp_file_path, null=True, blank=True)
    processing_type = models.CharField(max_length=20, choices=PROCESSING_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    result_text = models.TextField(blank=True, null=True)  # For OCR results
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Auto-delete files after expiration (24 hours)
    expiration_time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.processing_type} - {self.original_file.name}"
    
    def save(self, *args, **kwargs):
        # Set expiration time to 24 hours from now
        self.expiration_time = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete associated files when model instance is deleted
        if self.original_file:
            if os.path.isfile(self.original_file.path):
                os.remove(self.original_file.path)
        
        if self.processed_file:
            if os.path.isfile(self.processed_file.path):
                os.remove(self.processed_file.path)
                
        super().delete(*args, **kwargs)