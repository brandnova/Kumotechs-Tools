# cdn_tool/management/commands/cleanup_expired_files.py
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from cdn_tool.models import CDNFile

class Command(BaseCommand):
    help = 'Clean up expired CDN files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        expired_files = CDNFile.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=now
        )
        
        if not expired_files.exists():
            if options['verbose']:
                self.stdout.write(self.style.SUCCESS('No expired files found'))
            return

        expired_count = expired_files.count()
        
        if options['verbose']:
            self.stdout.write(f'Found {expired_count} expired files:')
            for file in expired_files:
                expired_days = (now - file.expires_at).days
                self.stdout.write(f'  - {file.get_display_name()} (expired {expired_days} days ago)')

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'Dry run - would delete {expired_count} expired files')
            )
            return

        # Delete files from disk and database
        deleted_count = 0
        for file in expired_files:
            try:
                # Delete from disk
                if file.file:
                    if hasattr(file.file, 'path') and os.path.exists(file.file.path):
                        os.remove(file.file.path)
                        if options['verbose']:
                            self.stdout.write(f'Deleted file: {file.file.path}')
                        
                        # Try to remove empty directories
                        try:
                            dir_path = os.path.dirname(file.file.path)
                            if os.path.exists(dir_path) and not os.listdir(dir_path):
                                os.rmdir(dir_path)
                                if options['verbose']:
                                    self.stdout.write(f'Removed empty directory: {dir_path}')
                                
                                # Try parent directory too
                                parent_dir = os.path.dirname(dir_path)
                                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                                    os.rmdir(parent_dir)
                                    if options['verbose']:
                                        self.stdout.write(f'Removed empty parent directory: {parent_dir}')
                        except OSError:
                            pass
                
                # Delete from database
                file_name = file.get_display_name()
                file.delete()
                deleted_count += 1
                
                if options['verbose']:
                    self.stdout.write(f'Deleted database record: {file_name}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error deleting {file.get_display_name()}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} expired files')
        )
        
        # Summary
        if options['verbose']:
            remaining_files = CDNFile.objects.count()
            self.stdout.write(f'Remaining files in database: {remaining_files}')
