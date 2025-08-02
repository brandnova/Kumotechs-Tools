# cdn_tool/views.py
import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.middleware.csrf import get_token
from .models import CDNFile
from .forms import FileUploadForm

def upload_page(request):
    """Upload page view"""
    form = FileUploadForm()
    recent_files = CDNFile.objects.all()[:5]
    
    context = {
        'form': form,
        'recent_files': recent_files,
    }
    
    return render(request, 'cdn_tool/upload.html', context)

def dashboard(request):
    """Main dashboard view with file management"""
    # Ensure CSRF token is available
    get_token(request)
    
    # Get search query
    search_query = request.GET.get('search', '')
    files_queryset = CDNFile.objects.all()
    
    if search_query:
        files_queryset = files_queryset.filter(
            Q(original_name__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(files_queryset, 12)  # Show 12 files per page
    page_number = request.GET.get('page')
    files = paginator.get_page(page_number)
    
    # Get file statistics - Fix total size calculation
    total_files = CDNFile.objects.count()
    total_size_bytes = CDNFile.objects.aggregate(total=Sum('file_size'))['total'] or 0
    
    # Format total size
    def format_total_size(bytes_size):
        if bytes_size == 0:
            return "0 Bytes"
        
        size_names = ["Bytes", "KB", "MB", "GB", "TB"]
        i = 0
        while bytes_size >= 1024 and i < len(size_names) - 1:
            bytes_size /= 1024.0
            i += 1
        
        return f"{bytes_size:.2f} {size_names[i]}"
    
    context = {
        'files': files,
        'search_query': search_query,
        'total_files': total_files,
        'total_size': format_total_size(total_size_bytes),
    }
    
    return render(request, 'cdn_tool/dashboard.html', context)

def search_files(request):
    """AJAX search endpoint"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)
        
        files_queryset = CDNFile.objects.all()
        
        if search_query:
            files_queryset = files_queryset.filter(
                Q(original_name__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(files_queryset, 12)
        files = paginator.get_page(page)
        
        # Render the files partial template
        files_html = render(request, 'cdn_tool/partials/files_list.html', {
            'files': files,
            'request': request
        }).content.decode('utf-8')
        
        return JsonResponse({
            'files_html': files_html,
            'has_next': files.has_next(),
            'has_previous': files.has_previous(),
            'current_page': files.number,
            'total_pages': files.paginator.num_pages,
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def upload_files(request):
    """Handle file uploads via AJAX"""
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        tags = request.POST.get('tags', '')
        description = request.POST.get('description', '')
        
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)
        
        # Define allowed file types and max size
        ALLOWED_TYPES = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
            'application/pdf', 'text/plain', 'text/csv',
            'application/zip', 'application/x-zip-compressed',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        
        uploaded_files = []
        
        for file in files:
            # Validate file size
            if file.size > MAX_FILE_SIZE:
                return JsonResponse({'error': f'File "{file.name}" is too large. Maximum size is 50MB.'}, status=400)
            
            # Validate file type
            if file.content_type not in ALLOWED_TYPES:
                return JsonResponse({'error': f'File type "{file.content_type}" is not allowed for file "{file.name}".'}, status=400)
            
            # Create CDN file record
            try:
                cdn_file = CDNFile(
                    file=file,
                    original_name=file.name,
                    file_type=file.content_type or 'application/octet-stream',
                    file_size=file.size,
                    tags=tags,
                    description=description
                )
                cdn_file.save()
                uploaded_files.append(cdn_file)
                
            except Exception as e:
                return JsonResponse({'error': f'Failed to save file "{file.name}": {str(e)}'}, status=500)
        
        # Render the recent uploads HTML
        recent_html = render(request, 'cdn_tool/partials/recent_uploads.html', {
            'recent_files': uploaded_files,
            'request': request
        }).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'recent_html': recent_html,
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def serve_file(request, hash_id):
    """Serve files via CDN URL with access tracking"""
    cdn_file = get_object_or_404(CDNFile, hash_id=hash_id)
    
    # Update last accessed time (but not download count for views)
    cdn_file.last_accessed = timezone.now()
    cdn_file.save(update_fields=['last_accessed'])
    
    try:
        if hasattr(cdn_file.file, 'path') and os.path.exists(cdn_file.file.path):
            file_path = cdn_file.file.path
        else:
            file_path = os.path.join(settings.MEDIA_ROOT, cdn_file.file.name)
        
        if not os.path.exists(file_path):
            raise Http404("File not found on disk")
        
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=cdn_file.file_type,
        )
        
        response['Content-Disposition'] = f'inline; filename="{cdn_file.original_name}"'
        response['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except (FileNotFoundError, OSError):
        raise Http404("File not found")

def download_file(request, hash_id):
    """Force download of files with usage tracking"""
    cdn_file = get_object_or_404(CDNFile, hash_id=hash_id)
    
    # Update usage stats
    cdn_file.increment_download_count()
    
    try:
        if hasattr(cdn_file.file, 'path') and os.path.exists(cdn_file.file.path):
            file_path = cdn_file.file.path
        else:
            file_path = os.path.join(settings.MEDIA_ROOT, cdn_file.file.name)
        
        if not os.path.exists(file_path):
            raise Http404("File not found on disk")
        
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=cdn_file.original_name
        )
        
        return response
        
    except (FileNotFoundError, OSError) as e:
        print(f"Download error: {e}")
        raise Http404("File not found")

@require_http_methods(["POST"])
def delete_file(request, file_id):
    """Delete a single file"""
    try:
        cdn_file = get_object_or_404(CDNFile, id=file_id)
        file_name = cdn_file.original_name
        
        # Delete the actual file from disk
        if cdn_file.file:
            try:
                if hasattr(cdn_file.file, 'path') and os.path.exists(cdn_file.file.path):
                    os.remove(cdn_file.file.path)
                    
                    # Also try to remove empty directories
                    try:
                        dir_path = os.path.dirname(cdn_file.file.path)
                        if os.path.exists(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            # Try to remove parent directory too if empty
                            parent_dir = os.path.dirname(dir_path)
                            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                                os.rmdir(parent_dir)
                    except OSError:
                        pass  # Directory not empty or other error
                        
            except (OSError, FileNotFoundError):
                pass  # File might already be deleted
        
        # Delete the database record
        cdn_file.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'File "{file_name}" deleted successfully'})
        
        messages.success(request, f'File "{file_name}" deleted successfully')
        return redirect('cdn_tool:dashboard')
        
    except Exception as e:
        print(f"Delete error: {e}")  # Debug print
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        
        messages.error(request, f'Error deleting file: {str(e)}')
        return redirect('cdn_tool:dashboard')

def file_details(request, file_id):
    """Get file details via AJAX"""
    cdn_file = get_object_or_404(CDNFile, id=file_id)
    
    return JsonResponse({
        'id': cdn_file.id,
        'name': cdn_file.original_name,
        'size': cdn_file.formatted_size,
        'type': cdn_file.file_type,
        'upload_date': cdn_file.upload_date.isoformat(),
        'cdn_url': request.build_absolute_uri(cdn_file.cdn_url),
        'download_url': request.build_absolute_uri(cdn_file.download_url),
        'html_snippet': cdn_file.html_snippet(request),
        'is_image': cdn_file.is_image,
        'tags': cdn_file.tags,
        'description': cdn_file.description,
        'download_count': cdn_file.download_count,
        'last_accessed': cdn_file.last_accessed.isoformat() if cdn_file.last_accessed else None,
        'file_icon': cdn_file.get_file_icon(),
    })

@require_http_methods(["POST"])
def bulk_delete(request):
    """Handle bulk delete of multiple files"""
    try:
        file_ids = request.POST.getlist('file_ids')
        
        if not file_ids:
            return JsonResponse({'success': False, 'error': 'No files selected'}, status=400)
        
        # Convert string IDs to integers
        try:
            file_ids = [int(id) for id in file_ids]
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid file IDs'}, status=400)
        
        files = CDNFile.objects.filter(id__in=file_ids)
        count = files.count()
        
        if count == 0:
            return JsonResponse({'success': False, 'error': 'No files found to delete'}, status=404)
        
        # Delete actual files from disk
        for file in files:
            if file.file:
                try:
                    if hasattr(file.file, 'path') and os.path.exists(file.file.path):
                        os.remove(file.file.path)
                        
                        # Try to remove empty directories
                        try:
                            dir_path = os.path.dirname(file.file.path)
                            if os.path.exists(dir_path) and not os.listdir(dir_path):
                                os.rmdir(dir_path)
                                parent_dir = os.path.dirname(dir_path)
                                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                                    os.rmdir(parent_dir)
                        except OSError:
                            pass
                except (OSError, FileNotFoundError):
                    pass
        
        # Delete database records
        files.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully deleted {count} file(s)',
            'deleted_count': count
        })
        
    except Exception as e:
        print(f"Bulk delete error: {e}")  # Debug print
        return JsonResponse({'success': False, 'error': f'Error deleting files: {str(e)}'}, status=500)
