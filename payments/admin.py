from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'farmer', 'match', 'amount_ngn', 'status', 'provider', 'paid_at']
    list_filter = ['status', 'provider']
