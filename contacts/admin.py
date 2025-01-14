from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'verified')
    list_filter = ('verified',)
    list_editable = ('verified',)
