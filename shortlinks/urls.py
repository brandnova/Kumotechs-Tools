from django.urls import path
from . import views

app_name = 'shortlinks'

urlpatterns = [
    path('shortener/', views.shortlink_dashboard, name='shortener'),
    path('delete/<int:pk>/', views.delete_shortlink, name='delete'),
    path('update/<int:pk>/', views.update_shortlink, name='update'),
    path('qr/<slug:slug>/', views.download_qr_code, name='download_qr'),
    path('qr/generate/<slug:slug>/', views.generate_qr_code_view, name='generate_qr'),
    path('qr/customize/<slug:slug>/', views.customize_qr_code,  name='generate_qr'),
    path('qr/customize/<slug:slug>/', views.customize_qr_code, name='customize_qr'),
]