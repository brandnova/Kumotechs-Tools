# cdn_tool/apps.py
from django.apps import AppConfig

class CdnToolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cdn_tool'
    verbose_name = 'CDN Tool'
