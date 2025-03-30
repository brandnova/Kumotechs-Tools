from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import WebsiteAnalysis
from .forms import WebsiteAnalysisForm
from .utils import analyze_website, capture_screenshot
import json
import time
import threading
import logging

logger = logging.getLogger(__name__)

@login_required
def analyzer_dashboard(request):
    """Dashboard view for the website analyzer"""
    analyses = WebsiteAnalysis.objects.filter(created_by=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = WebsiteAnalysisForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Check if this URL was recently analyzed by this user
            existing = WebsiteAnalysis.objects.filter(
                url=url, 
                created_by=request.user
            ).order_by('-created_at').first()
            
            # If analyzed in the last hour, use that result
            if existing and (time.time() - existing.created_at.timestamp()) < 3600:
                messages.info(request, f"Using recent analysis of {url}")
                return redirect('webanalyzer:detail', pk=existing.pk)
            
            # Analyze the website
            result = analyze_website(url)
            
            # Save the analysis
            analysis = WebsiteAnalysis(
                url=url,
                created_by=request.user,
                title=result.get('title'),
                description=result.get('description'),
                technologies=json.dumps(result.get('technologies', [])),
                server=result.get('server'),
                status_code=result.get('status_code'),
                response_time=result.get('response_time'),
                meta_tags=json.dumps(result.get('meta_tags', {})),
                social_media=json.dumps(result.get('social_media', [])),
                favicon=result.get('favicon'),
                mobile_friendly=result.get('mobile_friendly', False),
                page_size=result.get('page_size', 0),
            )
            analysis.save()
            
            # Capture screenshot in a separate thread to avoid blocking
            def capture_screenshot_thread(analysis_id, url):
                try:
                    capture_screenshot(url, analysis_id)
                except Exception as e:
                    logger.error(f"Error in screenshot thread: {e}")
            
            # Start the screenshot capture in a background thread
            thread = threading.Thread(
                target=capture_screenshot_thread,
                args=(analysis.pk, url)
            )
            thread.daemon = True
            thread.start()
            
            messages.success(request, f"Successfully analyzed {url}. Screenshot will be captured in the background.")
            return redirect('webanalyzer:detail', pk=analysis.pk)
    else:
        form = WebsiteAnalysisForm()
    
    context = {
        'analyses': analyses,
        'form': form,
    }
    return render(request, 'webanalyzer/dashboard.html', context)

@login_required
def analysis_detail(request, pk):
    """View details of a website analysis"""
    analysis = get_object_or_404(WebsiteAnalysis, pk=pk, created_by=request.user)
    
    context = {
        'analysis': analysis,
        'technologies': analysis.get_technologies_list(),
        'meta_tags': analysis.get_meta_tags(),
        'social_media': analysis.get_social_media_list(),
    }
    return render(request, 'webanalyzer/detail.html', context)

@login_required
def delete_analysis(request, pk):
    """Delete a website analysis"""
    analysis = get_object_or_404(WebsiteAnalysis, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        analysis.delete()
        messages.success(request, "Analysis deleted successfully!")
        return redirect('webanalyzer:dashboard')
    
    return redirect('webanalyzer:detail', pk=pk)

@login_required
def reanalyze_website(request, pk):
    """Re-analyze a previously analyzed website"""
    analysis = get_object_or_404(WebsiteAnalysis, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        # Analyze the website again
        result = analyze_website(analysis.url)
        
        # Update the analysis
        analysis.title = result.get('title')
        analysis.description = result.get('description')
        analysis.technologies = json.dumps(result.get('technologies', []))
        analysis.server = result.get('server')
        analysis.status_code = result.get('status_code')
        analysis.response_time = result.get('response_time')
        analysis.meta_tags = json.dumps(result.get('meta_tags', {}))
        analysis.social_media = json.dumps(result.get('social_media', []))
        analysis.favicon = result.get('favicon')
        analysis.mobile_friendly = result.get('mobile_friendly', False)
        analysis.page_size = result.get('page_size', 0)
        analysis.save()
        
        # Capture screenshot in a separate thread
        def capture_screenshot_thread(analysis_id, url):
            try:
                capture_screenshot(url, analysis_id)
            except Exception as e:
                logger.error(f"Error in screenshot thread: {e}")
        
        # Start the screenshot capture in a background thread
        thread = threading.Thread(
            target=capture_screenshot_thread,
            args=(analysis.pk, analysis.url)
        )
        thread.daemon = True
        thread.start()
        
        messages.success(request, f"Successfully re-analyzed {analysis.url}. Screenshot will be updated in the background.")
        
        return redirect('webanalyzer:detail', pk=analysis.pk)
    
    return redirect('webanalyzer:detail', pk=pk)

