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
    
    # User Journey URLs
    path('journeys/', views.journey_list, name='journey_list'),
    path('journeys/new/', views.create_journey, name='create_journey'),
    path('journeys/<int:pk>/', views.journey_detail, name='journey_detail'),
    path('journeys/<int:pk>/edit/', views.edit_journey, name='edit_journey'),
    path('journeys/<int:pk>/delete/', views.delete_journey, name='delete_journey'),
    path('journeys/<int:journey_pk>/steps/add/', views.add_journey_step, name='add_journey_step'),
    path('journeys/<int:journey_pk>/steps/<int:step_pk>/edit/', views.edit_journey_step, name='edit_journey_step'),
    path('journeys/<int:journey_pk>/steps/<int:step_pk>/delete/', views.delete_journey_step, name='delete_journey_step'),

    # Journey Templates
    path('templates/', views.template_list, name='template_list'),
    path('templates/<int:pk>/clone/', views.clone_template, name='clone_template'),
]