# academic_tools/urls.py
from django.urls import path
from . import views

app_name = 'academic_tools'

urlpatterns = [
    path('gpa-calculator/', views.gpa_calculator, name='gpa_calculator'),
    path('api/courses/', views.get_courses, name='get_courses'),
    path('api/calculate-gpa/', views.calculate_gpa, name='calculate_gpa'),
    path('api/calculate-cgpa/', views.calculate_cgpa, name='calculate_cgpa'),
]