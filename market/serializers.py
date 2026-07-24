from rest_framework import serializers
from .models import MarketPrice

class MarketPriceSerializer(serializers.ModelSerializer):
    crop_name = serializers.CharField(source='crop_type.name', read_only=True)
    hub_name = serializers.CharField(source='collection_point.name', read_only=True)
    last_updated = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = MarketPrice
        fields = ['id', 'crop_name', 'hub_name', 'price_per_kg', 'last_updated']

class TrendSerializer(serializers.Serializer):
    crop_name = serializers.CharField()
    trend_percentage = serializers.CharField()
    trend_direction = serializers.CharField()
    current_avg_price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2)

class MarketTrendResponseSerializer(serializers.Serializer):
    summary_alert = serializers.CharField()
    trends = TrendSerializer(many=True)
