from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FarmerProfile, BuyerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('AgriLink', {'fields': ('role', 'phone')}),
    )


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'state', 'lga', 'preferred_language', 'farm_size_hectares']
    list_filter = ['preferred_language', 'state']
    search_fields = ['user__username', 'state', 'lga']


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'location', 'verified_status']
    list_filter = ['verified_status']
    search_fields = ['user__username', 'business_name']
