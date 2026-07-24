from django.db import models
from django.conf import settings
from matching.models import Match


class DispatchRoute(models.Model):
    """A planned route for a dispatcher to pick up and deliver produce."""
    
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planned'
        IN_TRANSIT = 'in_transit', 'In Transit'
        DELIVERED = 'delivered', 'Delivered'

    dispatcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes',
        limit_choices_to={'role': 'dispatcher'},
    )
    matches = models.ManyToManyField(
        Match,
        related_name='routes',
    )
    route_waypoints = models.JSONField(
        default=list,
        help_text="List of waypoints in order: [{'type': 'pickup'|'delivery', 'lat': 0, 'lng': 0, 'name': ''}]"
    )
    estimated_distance_km = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    briefing_text = models.TextField(
        blank=True,
        help_text="AI-generated dispatch briefing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Route #{self.id} - {self.status}'
