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
    """Main dashboard view showing recent activity and counts from all tools"""

    # Get recent links and total count
    user_links = ShortLink.objects.filter(created_by=request.user)
    recent_links = user_links.order_by('-created_at')[:3]
    # total_links = user_links.count()

    # Get recent contacts and total count
    user_contacts = Contact.objects.filter(owner=request.user)
    recent_contacts = user_contacts.order_by('-created_at')[:3]
    # total_contacts = user_contacts.count()

    # Get recent media and total count
    user_media = ProcessedFile.objects.filter(user=request.user)
    recent_media = user_media.order_by('-created_at')[:3]
    # total_media = user_media.count()

    # Get recent website analyses and total count
    try:
        from webanalyzer.models import WebsiteAnalysis
        user_analyses = WebsiteAnalysis.objects.filter(created_by=request.user)
        recent_analyses = user_analyses.order_by('-created_at')[:3]
        # total_analyses = user_analyses.count()
    except:
        recent_analyses = []
        # total_analyses = 0

    context = {
        'recent_links': recent_links,
        'user_links': user_links,

        'recent_contacts': recent_contacts,
        'user_contacts': user_contacts,

        'recent_media': recent_media,
        'user_media': user_media,

        'recent_analyses': recent_analyses,
        'user_analyses': user_analyses,
    }

    return render(request, 'core/dashboard.html', context)
