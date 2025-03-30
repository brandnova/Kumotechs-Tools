from django.contrib import admin
from django.urls import path, include
from shortlinks.views import redirect_to_original
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('contacts/', include('contacts.urls')),
    path('shortlinks/', include('shortlinks.urls')),
    path('media-toolkit/', include('media_toolkit.urls', namespace='media_toolkit')),
    path('webanalyzer/', include('webanalyzer.urls', namespace='webanalyzer')),
    path('webtester/', include('webtester.urls', namespace='webtester')),
    
    # Redirect path for shortened URLs
    path('s/<slug:slug>/', redirect_to_original, name='shortlink_redirect'),
]

# Add this at the end of the file to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

