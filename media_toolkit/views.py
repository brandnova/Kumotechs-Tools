# media_toolkit/views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import ProcessedFile
from .forms import ImageUploadForm, PDFUploadForm
from .utils import (convert_image_format, compress_image, 
                   compress_pdf, extract_text_from_image)

@login_required
def dashboard(request):
    """Main dashboard for the Media Toolkit"""
    # Get user's recent files
    recent_files = ProcessedFile.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'image_form': ImageUploadForm(),
        'pdf_form': PDFUploadForm(),
        'recent_files': recent_files,
    }
    return render(request, 'media_toolkit/dashboard.html', context)

@login_required
@require_POST
def process_image(request):
    """Process uploaded image based on selected options"""
    form = ImageUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        # Create a ProcessedFile instance to track this upload
        processed_file = ProcessedFile(
            user=request.user,
            original_file=request.FILES['file'],
            status='processing'
        )
        
        # Determine the processing type
        if form.cleaned_data['perform_ocr']:
            processed_file.processing_type = 'ocr'
        elif form.cleaned_data['convert_format'] and form.cleaned_data['convert_format'] != '':
            processed_file.processing_type = 'format_conversion'
        elif form.cleaned_data['compress']:
            processed_file.processing_type = 'image_compression'
        else:
            # If no specific processing selected, default to format conversion
            processed_file.processing_type = 'format_conversion'
        
        processed_file.save()
        
        try:
            input_path = processed_file.original_file.path
            
            # Apply processing based on selected options
            if form.cleaned_data['perform_ocr']:
                output_path, file_name, text = extract_text_from_image(input_path)
                processed_file.result_text = text
                
                with open(output_path, 'rb') as f:
                    processed_file.processed_file.save(file_name, ContentFile(f.read()), save=True)
                os.remove(output_path)  # Clean up the temporary file
                
            elif form.cleaned_data['convert_format'] and form.cleaned_data['convert_format'] != '':
                output_path, file_name = convert_image_format(
                    input_path, 
                    output_format=form.cleaned_data['convert_format']
                )
                
                with open(output_path, 'rb') as f:
                    processed_file.processed_file.save(file_name, ContentFile(f.read()), save=True)
                os.remove(output_path)  # Clean up the temporary file
                
            elif form.cleaned_data['compress']:
                quality = form.cleaned_data['compression_quality'] or 85
                output_path, file_name = compress_image(input_path, quality=quality)
                
                with open(output_path, 'rb') as f:
                    processed_file.processed_file.save(file_name, ContentFile(f.read()), save=True)
                os.remove(output_path)  # Clean up the temporary file
            
            processed_file.status = 'completed'
            processed_file.save()
            
            return redirect(reverse('media_toolkit:file_detail', args=[processed_file.id]))
            
        except Exception as e:
            processed_file.status = 'failed'
            processed_file.result_text = str(e)
            processed_file.save()
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Invalid form submission'})

@login_required
@require_POST
def process_pdf(request):
    """Process uploaded PDF based on selected options"""
    form = PDFUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        # Create a ProcessedFile instance to track this upload
        processed_file = ProcessedFile(
            user=request.user,
            original_file=request.FILES['file'],
            processing_type='pdf_compression',
            status='processing'
        )
        processed_file.save()
        
        try:
            input_path = processed_file.original_file.path
            
            if form.cleaned_data['compress']:
                output_path, file_name = compress_pdf(input_path)
                
                with open(output_path, 'rb') as f:
                    processed_file.processed_file.save(file_name, ContentFile(f.read()))
            
            processed_file.status = 'completed'
            processed_file.save()
            
            return redirect(reverse('media_toolkit:file_detail', args=[processed_file.id]))
            
        except Exception as e:
            processed_file.status = 'failed'
            processed_file.result_text = str(e)
            processed_file.save()
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Invalid form submission'})

@login_required
def file_detail(request, file_id):
    """View details of a processed file and download options"""
    processed_file = get_object_or_404(ProcessedFile, id=file_id, user=request.user)
    
    return render(request, 'media_toolkit/file_detail.html', {
        'file': processed_file,
    })

@login_required
def download_file(request, file_id):
    """Download a processed file"""
    processed_file = get_object_or_404(ProcessedFile, id=file_id, user=request.user)
    
    if processed_file.processed_file:
        file_path = processed_file.processed_file.path
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    
    return HttpResponse("File not available")

@login_required
def file_list(request):
    """View list of all processed files for current user"""
    files = ProcessedFile.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'media_toolkit/file_list.html', {
        'files': files,
    })

@login_required
def delete_file(request, file_id):
    """Delete a processed file"""
    processed_file = get_object_or_404(ProcessedFile, id=file_id, user=request.user)
    processed_file.delete()
    
    return redirect(reverse('media_toolkit:file_list'))