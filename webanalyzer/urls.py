from django.urls import path
from . import views

app_name = 'webanalyzer'

urlpatterns = [
    path('', views.analyzer_dashboard, name='dashboard'),
    path('analysis/<int:pk>/', views.analysis_detail, name='detail'),
    path('analysis/<int:pk>/delete/', views.delete_analysis, name='delete'),
    path('analysis/<int:pk>/reanalyze/', views.reanalyze_website, name='reanalyze'),
]

