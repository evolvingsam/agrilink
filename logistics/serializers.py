from rest_framework import serializers
from .models import DispatchRoute
from matching.models import Match


class RouteMatchSerializer(serializers.ModelSerializer):
    """Lightweight match summary embedded in route responses."""
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    farmer_name = serializers.CharField(source='listing.farmer.username', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)

    class Meta:
        model = Match
        fields = ['id', 'order_id', 'farmer_name', 'order_status', 'status']


class DispatchRouteSerializer(serializers.ModelSerializer):
    dispatcher_name = serializers.CharField(source='dispatcher.username', read_only=True)
    matches = RouteMatchSerializer(many=True, read_only=True)

    class Meta:
        model = DispatchRoute
        fields = [
            'id', 'dispatcher', 'dispatcher_name', 'matches',
            'route_waypoints', 'estimated_distance_km', 'status',
            'briefing_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'dispatcher', 'matches', 'route_waypoints', 'estimated_distance_km', 'briefing_text', 'created_at']
