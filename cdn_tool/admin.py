# cdn_tool/admin.py
from django.contrib import admin
from .models import CDNFile

@admin.register(CDNFile)
class CDNFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'file_type', 'formatted_size', 'upload_date', 'download_count')
    list_filter = ('file_type', 'upload_date')
    search_fields = ('original_name', 'tags', 'description')
    readonly_fields = ('hash_id', 'file_size', 'upload_date', 'last_accessed', 'download_count')
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'original_name', 'file_type', 'file_size', 'hash_id')
        }),
        ('Metadata', {
            'fields': ('tags', 'description')
        }),
        ('Statistics', {
            'fields': ('upload_date', 'last_accessed', 'download_count')
        }),
    )
    
    def formatted_size(self, obj):
        return obj.formatted_size
    formatted_size.short_description = 'File Size'
