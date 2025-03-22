# media_toolkit/urls.py
from django.urls import path
from . import views

app_name = 'media_toolkit'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('process-image/', views.process_image, name='process_image'),
    path('process-pdf/', views.process_pdf, name='process_pdf'),
    path('files/', views.file_list, name='file_list'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),
    path('file/<int:file_id>/download/', views.download_file, name='download_file'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
]