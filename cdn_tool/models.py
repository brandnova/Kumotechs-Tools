# cdn_tool/models.py
import os
import hashlib
import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone

def upload_to_hashed_path(instance, filename):
    """Generate a hashed path for uploaded files"""
    # Create a hash based on the file content and timestamp
    hash_object = hashlib.md5(f"{filename}{timezone.now()}".encode())
    hash_hex = hash_object.hexdigest()
    
    # Create directory structure: cdn_files/ab/cd/abcd1234.ext
    return f"cdn_files/{hash_hex[:2]}/{hash_hex[2:4]}/{hash_hex}.{filename.split('.')[-1]}"

class CDNFile(models.Model):
    # File storage
    file = models.FileField(upload_to=upload_to_hashed_path)
    
    # Metadata
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    
    # Unique identifier for URLs
    hash_id = models.CharField(max_length=32, unique=True, db_index=True)
    
    # Optional fields for organization
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    description = models.TextField(blank=True)
    
    # Usage tracking
    download_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-upload_date']
        verbose_name = "CDN File"
        verbose_name_plural = "CDN Files"

    def __str__(self):
        return self.original_name

    def save(self, *args, **kwargs):
        if not self.hash_id:
            self.hash_id = str(uuid.uuid4()).replace('-', '')[:16]
        super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.file_type.startswith('image/')

    @property
    def is_pdf(self):
        return 'pdf' in self.file_type.lower()

    @property
    def is_archive(self):
        return any(ext in self.file_type.lower() for ext in ['zip', 'rar', '7z', 'tar', 'gz'])

    @property
    def is_document(self):
        return any(ext in self.file_type.lower() for ext in ['doc', 'docx', 'txt', 'rtf'])

    @property
    def cdn_url(self):
        return f"{self.hash_id}/"

    @property
    def download_url(self):
        return f"{self.hash_id}/download/"

    def html_snippet(self, request=None):
        """Generate HTML snippet for the file"""
        if self.is_image:
            if request:
                full_url = request.build_absolute_uri(self.cdn_url)
            else:
                # Simple fallback without using Sites framework
                full_url = f"http://localhost:8000{self.cdn_url}"
            return f'<img src="{full_url}" alt="{self.original_name}" />'
        return None

    def get_full_cdn_url(self, request=None):
        """Get full CDN URL with domain"""
        if request:
            return request.build_absolute_uri(self.cdn_url)
        return f"http://localhost:8000{self.cdn_url}"

    def get_full_download_url(self, request=None):
        """Get full download URL with domain"""
        if request:
            return request.build_absolute_uri(self.download_url)
        return f"http://localhost:8000{self.download_url}"

    @property
    def formatted_size(self):
        """Format file size in human readable format"""
        bytes_size = self.file_size
        if bytes_size == 0:
            return "0 Bytes"
        
        size_names = ["Bytes", "KB", "MB", "GB", "TB"]
        i = 0
        while bytes_size >= 1024 and i < len(size_names) - 1:
            bytes_size /= 1024.0
            i += 1
        
        return f"{bytes_size:.2f} {size_names[i]}"

    def get_file_icon(self):
        """Get appropriate icon class for file type"""
        if self.is_image:
            return 'image'
        elif self.is_pdf:
            return 'file-pdf'
        elif self.is_document:
            return 'file-text'
        elif self.is_archive:
            return 'file-archive'
        else:
            return 'file'

    def increment_download_count(self):
        """Increment download count and update last accessed"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])
