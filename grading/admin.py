from django.contrib import admin
from .models import GradingResult


@admin.register(GradingResult)
class GradingResultAdmin(admin.ModelAdmin):
    list_display = ['listing', 'grade', 'estimated_shelf_days', 'confidence', 'graded_at']
    list_filter = ['grade']
    readonly_fields = ['listing', 'grade', 'issues', 'estimated_shelf_days', 'confidence', 'raw_response', 'graded_at']
