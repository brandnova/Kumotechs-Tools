# media_toolkit/management/commands/cleanup_expired_files.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from media_toolkit.models import ProcessedFile

class Command(BaseCommand):
    help = 'Clean up expired processed files'

    def handle(self, *args, **options):
        # Find files that have expired
        expired_files = ProcessedFile.objects.filter(
            expiration_time__lt=timezone.now()
        )
        
        count = expired_files.count()
        # Delete expired files
        for file in expired_files:
            file.delete()
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {count} expired files')
        )