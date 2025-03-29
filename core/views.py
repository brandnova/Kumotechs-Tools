from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shortlinks.models import ShortLink
from contacts.models import Contact
from media_toolkit.models import ProcessedFile

def home_view(request):
    return render(request, 'core/home.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def dashboard(request):
    """Main dashboard view showing recent activity from all tools"""
    # Get recent links (last 3)
    recent_links = ShortLink.objects.filter(created_by=request.user).order_by('-created_at')[:3]
    
    # Get recent contacts (last 3)
    recent_contacts = Contact.objects.filter(owner=request.user).order_by('-created_at')[:3]

    # Get recent Media (last 3)
    recent_media = ProcessedFile.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    # Get recent website analyses (last 3)
    try:
        from webanalyzer.models import WebsiteAnalysis
        recent_analyses = WebsiteAnalysis.objects.filter(created_by=request.user).order_by('-created_at')[:3]
    except:
        recent_analyses = []
    
    context = {
        'recent_links': recent_links,
        'recent_contacts': recent_contacts,
        'recent_media': recent_media,
        'recent_analyses': recent_analyses,
    }
    
    return render(request, 'core/dashboard.html', context)