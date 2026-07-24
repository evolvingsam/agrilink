from rest_framework import serializers
from .models import DispatchRoute

class DispatchRouteSerializer(serializers.ModelSerializer):
    dispatcher_name = serializers.CharField(source='dispatcher.username', read_only=True)

    class Meta:
        model = DispatchRoute
        fields = [
            'id', 'dispatcher', 'dispatcher_name', 'matches',
            'route_waypoints', 'estimated_distance_km', 'status',
            'briefing_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'dispatcher', 'matches', 'route_waypoints', 'estimated_distance_km', 'briefing_text', 'created_at']
