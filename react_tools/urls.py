from django.urls import path
from . import views

app_name = 'react_tools'

urlpatterns = [
    path('notes/', views.notes_view, name='notes'),
    path('uuid/', views.uuid_view, name='uuid'),
    path('json/', views.json_formatter, name='json_formatter'),
]