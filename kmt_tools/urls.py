from django.contrib import admin
from django.urls import path, include
from shortlinks.views import redirect_to_original

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('contacts/', include('contacts.urls')),
    path('shortlinks/', include('shortlinks.urls')),
    path('media-toolkit/', include('media_toolkit.urls', namespace='media_toolkit')),
    
    # Redirect path for shortened URLs
    path('s/<slug:slug>/', redirect_to_original, name='shortlink_redirect'),
]