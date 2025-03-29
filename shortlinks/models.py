from django.db import models
from django.contrib.auth.models import User
import random
import string
import os

class ShortLink(models.Model):
    original_url = models.URLField(max_length=2000)
    slug = models.SlugField(max_length=15, unique=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True, help_text="A friendly name to identify this link")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shortlinks')
    created_at = models.DateTimeField(auto_now_add=True)
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    has_custom_qr = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.name:
            return f"{self.name} ({self.slug})"
        return f"{self.slug} -> {self.original_url[:50]}"
    
    def save(self, *args, **kwargs):
        # Generate a slug if one doesn't exist
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self, length=6):
        """Generate a unique random slug for the URL"""
        chars = string.ascii_letters + string.digits
        while True:
            slug = ''.join(random.choice(chars) for _ in range(length))
            if not ShortLink.objects.filter(slug=slug).exists():
                return slug
    
    def delete(self, *args, **kwargs):
        # Delete the QR code file if it exists
        if self.qr_code:
            if os.path.isfile(self.qr_code.path):
                os.remove(self.qr_code.path)
        
        # Delete any customization if it exists
        try:
            if hasattr(self, 'qr_customization'):
                self.qr_customization.delete()
        except:
            pass
            
        super().delete(*args, **kwargs)

class QRCodeCustomization(models.Model):
    shortlink = models.OneToOneField(ShortLink, on_delete=models.CASCADE, related_name='qr_customization')
    color = models.CharField(max_length=20, default='#000000')
    bg_color = models.CharField(max_length=20, default='#FFFFFF')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    convert_logo_bw = models.BooleanField(default=False, help_text="Convert logo to black and white")
    text = models.CharField(max_length=50, blank=True, null=True, help_text="Text to display below the QR code")
    
    def __str__(self):
        return f"QR Customization for {self.shortlink.slug}"
    
    def delete(self, *args, **kwargs):
        # Delete the logo file if it exists
        if self.logo:
            if os.path.isfile(self.logo.path):
                os.remove(self.logo.path)
        super().delete(*args, **kwargs)

