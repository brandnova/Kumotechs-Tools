# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("manage/", views.manage_contacts, name="manage_contacts"),
    path("manage/create/", views.create_contact, name="create_contact"),
    path("manage/<int:contact_id>/update/", views.update_contact, name="update_contact"),
    path("manage/<int:contact_id>/delete/", views.delete_contact, name="delete_contact"),
    path("api/submit-contact/", views.public_submit_contact, name="public_submit_contact"),
    path("export-vcf/", views.export_vcf, name="export_vcf"),
]