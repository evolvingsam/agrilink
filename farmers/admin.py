from django.contrib import admin
from .models import CropType, CollectionPoint, ProduceListing


@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'typical_shelf_life_days', 'perishability_score']
    search_fields = ['name']


@admin.register(CollectionPoint)
class CollectionPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'lga', 'has_cold_storage', 'solar_powered']
    list_filter = ['state', 'has_cold_storage', 'solar_powered']
    search_fields = ['name', 'state', 'lga']


@admin.register(ProduceListing)
class ProduceListingAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'crop_type', 'quantity_kg', 'price_per_kg', 'quality_grade', 'status', 'harvest_date']
    list_filter = ['status', 'quality_grade', 'crop_type']
    search_fields = ['farmer__username', 'crop_type__name']
    readonly_fields = ['quality_grade', 'status', 'created_at', 'updated_at']
