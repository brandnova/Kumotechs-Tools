from django.urls import path
from . import views

app_name = 'shortlinks'

urlpatterns = [
    path('dashboard/', views.shortlink_dashboard, name='dashboard'),
    path('delete/<int:pk>/', views.delete_shortlink, name='delete'),
]