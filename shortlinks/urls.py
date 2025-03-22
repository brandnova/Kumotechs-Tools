from django.urls import path
from . import views

app_name = 'shortlinks'

urlpatterns = [
    path('shortener/', views.shortlink_dashboard, name='shortener'),
    path('delete/<int:pk>/', views.delete_shortlink, name='delete'),
]