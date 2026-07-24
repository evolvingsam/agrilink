from rest_framework import serializers
from .models import GradingResult


class GradingResultSerializer(serializers.ModelSerializer):
    listing_id = serializers.IntegerField(source='listing.id', read_only=True)
    crop_name = serializers.CharField(source='listing.crop_type.name', read_only=True)

    class Meta:
        model = GradingResult
        fields = [
            'id', 'listing_id', 'crop_name',
            'grade', 'issues', 'estimated_shelf_days',
            'confidence', 'graded_at',
        ]
        read_only_fields = fields
