# cdn_tool/urls.py
from django.urls import path
from . import views

app_name = 'cdn_tool'

urlpatterns = [
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_page, name='upload'),
    
    # AJAX endpoints
    path('api/search/', views.search_files, name='search_files'),
    path('api/upload/', views.upload_files, name='upload_files'),
    path('api/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('api/details/<int:file_id>/', views.file_details, name='file_details'),
    # Bulk operations
    path('api/bulk-delete/', views.bulk_delete, name='bulk_delete'),
    
    # CDN serving URLs - These must match the model properties exactly
    path('<str:hash_id>/', views.serve_file, name='serve_file'),
    path('<str:hash_id>/download/', views.download_file, name='download_file'),
]
