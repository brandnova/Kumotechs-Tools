from django.urls import path
from . import views

app_name = 'webtester'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('test/new/', views.create_test, name='create'),
    path('test/<int:pk>/', views.test_detail, name='detail'),
    path('test/<int:pk>/edit/', views.edit_test, name='edit'),
    path('test/<int:pk>/run/', views.run_test, name='run'),
    path('test/<int:pk>/delete/', views.delete_test, name='delete'),
    path('test/<int:pk>/status/', views.test_status, name='status'),
    path('test/<int:pk>/clone/', views.clone_test, name='clone'),
]

