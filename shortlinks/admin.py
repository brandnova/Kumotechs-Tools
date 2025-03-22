from django.contrib import admin
from .models import ShortLink

@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('slug', 'truncated_url', 'created_by', 'created_at', 'access_count', 'last_accessed')
    list_filter = ('created_at', 'created_by')
    search_fields = ('original_url', 'slug')
    readonly_fields = ('access_count', 'last_accessed')
    
    def truncated_url(self, obj):
        return obj.original_url[:50] + '...' if len(obj.original_url) > 50 else obj.original_url
    truncated_url.short_description = 'Original URL'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)