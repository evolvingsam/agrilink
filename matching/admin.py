from django.contrib import admin
from .models import BuyerOrder, Match


@admin.register(BuyerOrder)
class BuyerOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'crop_type', 'quantity_kg', 'status', 'required_grade']
    list_filter = ['status', 'crop_type', 'required_grade']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'order', 'status', 'match_score']
    list_filter = ['status']
