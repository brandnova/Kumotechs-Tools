from django.contrib import admin
from .models import LoadTest, UserJourney, JourneyStep, TestAssignment

class TestAssignmentInline(admin.TabularInline):
    model = TestAssignment
    extra = 1

class LoadTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'created_by')
    search_fields = ('name', 'target_url')
    inlines = [TestAssignmentInline]

class JourneyStepInline(admin.TabularInline):
    model = JourneyStep
    extra = 1

class UserJourneyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'base_url', 'created_at')
    list_filter = ('created_by',)
    search_fields = ('name', 'base_url')
    inlines = [JourneyStepInline]

admin.site.register(LoadTest, LoadTestAdmin)
admin.site.register(UserJourney, UserJourneyAdmin)
admin.site.register(TestAssignment)