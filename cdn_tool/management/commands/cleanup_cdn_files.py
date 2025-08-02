# cdn_tool/management/commands/cleanup_cdn_files.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from cdn_tool.models import CDNFile

class Command(BaseCommand):
    help = 'Clean up orphaned CDN files that exist on disk but not in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        cdn_files_path = os.path.join(settings.MEDIA_ROOT, 'cdn_files')
        
        if not os.path.exists(cdn_files_path):
            self.stdout.write(self.style.WARNING('CDN files directory does not exist'))
            return

        # Get all file paths from database
        db_files = set()
        for cdn_file in CDNFile.objects.all():
            if cdn_file.file:
                db_files.add(cdn_file.file.path)

        # Walk through all files in cdn_files directory
        orphaned_files = []
        for root, dirs, files in os.walk(cdn_files_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in db_files:
                    orphaned_files.append(file_path)

        if not orphaned_files:
            self.stdout.write(self.style.SUCCESS('No orphaned files found'))
            return

        self.stdout.write(f'Found {len(orphaned_files)} orphaned files:')
        for file_path in orphaned_files:
            self.stdout.write(f'  - {file_path}')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run - no files were deleted'))
        else:
            deleted_count = 0
            for file_path in orphaned_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    self.stdout.write(f'Deleted: {file_path}')
                except OSError as e:
                    self.stdout.write(self.style.ERROR(f'Error deleting {file_path}: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} orphaned files'))

            # Clean up empty directories
            for root, dirs, files in os.walk(cdn_files_path, topdown=False):
                if not files and not dirs and root != cdn_files_path:
                    try:
                        os.rmdir(root)
                        self.stdout.write(f'Removed empty directory: {root}')
                    except OSError:
                        pass
