from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'owner', 'verified')
    list_filter = ('verified', 'owner')
    list_editable = ('verified',)
    search_fields = ('name', 'email', 'phone', 'organization')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.owner = request.user
        super().save_model(request, obj, form, change)