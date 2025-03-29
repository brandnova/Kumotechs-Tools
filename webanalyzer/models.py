from django.db import models
from django.contrib.auth.models import User
import json

class WebsiteAnalysis(models.Model):
    url = models.URLField(max_length=2000)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='website_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    server = models.CharField(max_length=255, blank=True, null=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    meta_tags = models.TextField(blank=True, null=True)
    social_media = models.TextField(blank=True, null=True)
    favicon = models.URLField(max_length=2000, blank=True, null=True)
    mobile_friendly = models.BooleanField(default=False)
    page_size = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Website Analysis'
        verbose_name_plural = 'Website Analyses'
    
    def __str__(self):
        return f"Analysis of {self.url}"
    
    def get_technologies_list(self):
        if not self.technologies:
            return []
        try:
            return json.loads(self.technologies)
        except:
            return []
    
    def get_technologies_display(self):
        techs = self.get_technologies_list()
        if not techs:
            return "No technologies detected"
        return ", ".join(techs)
    
    def get_status_display(self):
        if not self.status_code:
            return "Unknown"
        
        if 200 <= self.status_code < 300:
            return f"{self.status_code} (Success)"
        elif 300 <= self.status_code < 400:
            return f"{self.status_code} (Redirect)"
        elif 400 <= self.status_code < 500:
            return f"{self.status_code} (Client Error)"
        elif 500 <= self.status_code < 600:
            return f"{self.status_code} (Server Error)"
        else:
            return f"{self.status_code} (Unknown)"
    
    def get_meta_tags(self):
        if not self.meta_tags:
            return {}
        try:
            return json.loads(self.meta_tags)
        except:
            return {}
    
    def get_social_media_list(self):
        if not self.social_media:
            return []
        try:
            return json.loads(self.social_media)
        except:
            return []
    
    def get_page_size_display(self):
        """Return page size in a human-readable format"""
        if self.page_size < 1024:
            return f"{self.page_size} bytes"
        elif self.page_size < 1024 * 1024:
            return f"{self.page_size / 1024:.1f} KB"
        else:
            return f"{self.page_size / (1024 * 1024):.1f} MB"

