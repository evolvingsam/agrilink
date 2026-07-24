from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.username', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'farmer', 'farmer_name', 'match', 'amount_ngn',
            'status', 'transaction_ref', 'provider', 'paid_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields
