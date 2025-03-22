# media_toolkit/admin.py
from django.contrib import admin
from .models import ProcessedFile

@admin.register(ProcessedFile)
class ProcessedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'processing_type', 'status', 'created_at', 'expiration_time')
    list_filter = ('processing_type', 'status', 'created_at')
    search_fields = ('user__username', 'original_file', 'processed_file')
    readonly_fields = ('created_at', 'updated_at', 'expiration_time')