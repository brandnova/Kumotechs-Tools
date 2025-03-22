from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from .models import ShortLink
from .forms import ShortLinkForm

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
    
    context = {
        'links': links,
        'form': form,
        'base_url': base_url,
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