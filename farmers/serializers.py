from rest_framework import serializers
from .models import CropType, CollectionPoint, ProduceListing


class CropTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropType
        fields = ['id', 'name', 'typical_shelf_life_days', 'perishability_score']


class CollectionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPoint
        fields = [
            'id', 'name', 'state', 'lga', 'address',
            'has_cold_storage', 'solar_powered',
            'latitude', 'longitude',
        ]


class ProduceListingSerializer(serializers.ModelSerializer):
    crop_name = serializers.CharField(source='crop_type.name', read_only=True)
    farmer_name = serializers.CharField(source='farmer.username', read_only=True)
    collection_point_name = serializers.CharField(
        source='collection_point.name', read_only=True
    )

    class Meta:
        model = ProduceListing
        fields = [
            'id', 'farmer', 'farmer_name', 'crop_type', 'crop_name',
            'collection_point', 'collection_point_name',
            'quantity_kg', 'price_per_kg', 'harvest_date',
            'status', 'quality_grade', 'photo', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'farmer', 'farmer_name', 'crop_name',
            'collection_point_name', 'status', 'quality_grade',
            'created_at', 'updated_at',
        ]

    def create(self, validated_data):
        # Attach the current user as the farmer automatically
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)


class PhotoUploadSerializer(serializers.ModelSerializer):
    """Used only for the photo upload endpoint."""
    class Meta:
        model = ProduceListing
        fields = ['photo']
