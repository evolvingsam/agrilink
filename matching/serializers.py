from rest_framework import serializers
from .models import BuyerOrder, Match


class BuyerOrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    crop_name = serializers.CharField(source='crop_type.name', read_only=True)

    class Meta:
        model = BuyerOrder
        fields = [
            'id', 'buyer', 'buyer_name', 'crop_type', 'crop_name',
            'quantity_kg', 'max_price_per_kg', 'required_grade',
            'status', 'created_at',
        ]
        read_only_fields = ['id', 'buyer', 'status', 'created_at']


class MatchSerializer(serializers.ModelSerializer):
    listing_id = serializers.IntegerField(source='listing.id', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    farmer_name = serializers.CharField(source='listing.farmer.username', read_only=True)
    buyer_name = serializers.CharField(source='order.buyer.username', read_only=True)
    price_per_kg = serializers.DecimalField(
        source='listing.price_per_kg', max_digits=10, decimal_places=2, read_only=True
    )
    quality_grade = serializers.CharField(source='listing.quality_grade', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'listing_id', 'order_id', 'farmer_name', 'buyer_name',
            'price_per_kg', 'quality_grade', 'match_score', 'status', 'created_at',
        ]
        read_only_fields = fields
