from django.contrib import admin
from .models import DispatchRoute

@admin.register(DispatchRoute)
class DispatchRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'dispatcher', 'status', 'estimated_distance_km', 'created_at']
    list_filter = ['status']
    raw_id_fields = ['dispatcher']
    filter_horizontal = ['matches']
