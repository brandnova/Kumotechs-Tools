from django.db import models
from django.contrib.auth.models import User
import random
import string

class ShortLink(models.Model):
    original_url = models.URLField(max_length=2000)
    slug = models.SlugField(max_length=15, unique=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shortlinks')
    created_at = models.DateTimeField(auto_now_add=True)
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
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