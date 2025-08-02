from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from .models import ShortLink, QRCodeCustomization
from .forms import ShortLinkForm, QRCodeCustomizationForm
from .utils import generate_qr_code, save_qr_code, process_logo
import os
import json

@login_required
def shortlink_dashboard(request):
    """Dashboard view showing all of a user's shortened URLs"""
    links = ShortLink.objects.filter(created_by=request.user)
    
    base_url = request.build_absolute_uri('/').rstrip('/') + '/s/'
    
    if request.method == 'POST':
        form = ShortLinkForm(request.POST)
        if form.is_valid():
            shortlink = form.save(commit=False)
            shortlink.created_by = request.user
            shortlink.save()
            
            messages.success(request, "URL shortened successfully!")
            return redirect('shortlinks:shortener')
    else:
        form = ShortLinkForm()
    
    # Create QR customization form
    qr_form = QRCodeCustomizationForm()
    
    # Calculate statistics
    total_links = links.count()
    total_clicks = links.aggregate(total=Sum('access_count'))['total'] or 0
    total_qr_codes = links.filter(qr_code__isnull=False).exclude(qr_code='').count()
    
    context = {
        'links': links,
        'form': form,
        'qr_form': qr_form,
        'base_url': base_url,
        'total_links': total_links,
        'total_clicks': total_clicks,
        'total_qr_codes': total_qr_codes,
    }
    return render(request, 'shortlinks/shortener.html', context)

def redirect_to_original(request, slug):
    """Redirect users from short link to the original URL"""
    shortlink = get_object_or_404(ShortLink, slug=slug)
    shortlink.access_count += 1
    shortlink.last_accessed = timezone.now()
    shortlink.save()
    return redirect(shortlink.original_url)

@login_required
def delete_shortlink(request, pk):
    """Delete a short URL"""
    shortlink = get_object_or_404(ShortLink, pk=pk, created_by=request.user)
    if request.method == 'POST':
        shortlink.delete()
        messages.success(request, "Short URL deleted successfully!")
    return redirect('shortlinks:shortener')

@login_required
def generate_qr_code_view(request, slug):
    """Generate QR code for a short URL"""
    if request.method == 'POST':
        shortlink = get_object_or_404(ShortLink, slug=slug, created_by=request.user)
        
        # Get form data
        data = json.loads(request.body)
        color = data.get('color', '#000000')
        bg_color = data.get('bg_color', '#FFFFFF')
        text = data.get('text', '')
        convert_bw = data.get('convert_bw', False)
        
        # Generate QR code
        base_url = request.build_absolute_uri('/').rstrip('/') + '/s/'
        short_url = f"{base_url}{shortlink.slug}"
        
        # Check if there's a customization for this shortlink
        try:
            customization = shortlink.qr_customization
            logo_path = customization.logo.path if customization.logo else None
        except QRCodeCustomization.DoesNotExist:
            logo_path = None
        
        # Generate QR code as base64
        qr_base64 = generate_qr_code(
            short_url, 
            logo_path=logo_path,
            color=color,
            bg_color=bg_color,
            text=text,
            convert_bw=convert_bw
        )
        
        return JsonResponse({'qr_code': qr_base64})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def customize_qr_code(request, slug):
    """Customize QR code for a short URL"""
    shortlink = get_object_or_404(ShortLink, slug=slug, created_by=request.user)
    
    if request.method == 'POST':
        # Check if there's an existing customization
        try:
            customization = shortlink.qr_customization
        except QRCodeCustomization.DoesNotExist:
            customization = QRCodeCustomization(shortlink=shortlink)
        
        form = QRCodeCustomizationForm(request.POST, request.FILES, instance=customization)
        
        if form.is_valid():
            # Process logo if provided
            if 'logo' in request.FILES:
                logo_file = request.FILES['logo']
                logo_filename = f"{shortlink.slug}_logo.png"
                logo_path = process_logo(logo_file, logo_filename)
                
                if logo_path:
                    customization.logo = logo_path
            
            customization.color = form.cleaned_data['color']
            customization.bg_color = form.cleaned_data['bg_color']
            customization.convert_logo_bw = form.cleaned_data['convert_logo_bw']
            customization.text = form.cleaned_data['text']
            customization.save()
            
            # Mark shortlink as having custom QR
            shortlink.has_custom_qr = True
            shortlink.save()
            
            # Generate and save the QR code
            base_url = request.build_absolute_uri('/').rstrip('/') + '/s/'
            short_url = f"{base_url}{shortlink.slug}"
            qr_filename = f"{shortlink.slug}.png"
            
            logo_path = customization.logo.path if customization.logo else None
            
            qr_path = save_qr_code(
                short_url, 
                qr_filename,
                logo_path=logo_path,
                color=customization.color,
                bg_color=customization.bg_color,
                text=customization.text,
                convert_bw=customization.convert_logo_bw
            )
            
            # Save the QR code path to the model
            shortlink.qr_code = qr_path
            shortlink.save()
            
            messages.success(request, "QR code customized successfully!")
            return redirect('shortlinks:shortener')
        else:
            messages.error(request, "Error customizing QR code. Please check the form.")
    
    return redirect('shortlinks:shortener')

@login_required
def download_qr_code(request, slug):
    """Download QR code for a short URL"""
    shortlink = get_object_or_404(ShortLink, slug=slug, created_by=request.user)
    
    if not shortlink.qr_code:
        # If QR code doesn't exist, create a default one
        base_url = request.build_absolute_uri('/').rstrip('/') + '/s/'
        short_url = f"{base_url}{shortlink.slug}"
        qr_filename = f"{shortlink.slug}.png"
        
        # Check if there's a customization
        try:
            customization = shortlink.qr_customization
            logo_path = customization.logo.path if customization.logo else None
            color = customization.color
            bg_color = customization.bg_color
            text = customization.text
            convert_bw = customization.convert_logo_bw
        except QRCodeCustomization.DoesNotExist:
            logo_path = None
            color = "black"
            bg_color = "white"
            text = None
            convert_bw = False
        
        qr_path = save_qr_code(
            short_url, 
            qr_filename,
            logo_path=logo_path,
            color=color,
            bg_color=bg_color,
            text=text,
            convert_bw=convert_bw
        )
        
        # Save the QR code path to the model
        shortlink.qr_code = qr_path
        shortlink.save()
    
    # Serve the file
    with open(shortlink.qr_code.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{shortlink.slug}_qr.png"'
        return response

@login_required
def update_shortlink(request, pk):
    """Update a short URL's name"""
    shortlink = get_object_or_404(ShortLink, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        shortlink.name = name
        shortlink.save()
        messages.success(request, "Link name updated successfully!")
    
    return redirect('shortlinks:shortener')

