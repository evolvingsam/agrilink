from django.db import models
from django.conf import settings
from farmers.models import CropType, ProduceListing


class BuyerOrder(models.Model):
    """An order placed by a buyer for a specific crop and grade."""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        MATCHED = 'matched', 'Matched'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'buyer'},
    )
    crop_type = models.ForeignKey(
        CropType,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    max_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    required_grade = models.CharField(
        max_length=10,
        choices=ProduceListing.Grade.choices,
        default=ProduceListing.Grade.B,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} - {self.buyer.username} - {self.crop_type.name}'


class Match(models.Model):
    """A match between a buyer order and a produce listing."""

    class Status(models.TextChoices):
        PENDING_DELIVERY = 'pending_delivery', 'Pending Delivery'
        DELIVERED = 'delivered', 'Delivered'

    listing = models.ForeignKey(
        ProduceListing,
        on_delete=models.PROTECT,
        related_name='matches',
    )
    order = models.ForeignKey(
        BuyerOrder,
        on_delete=models.PROTECT,
        related_name='matches',
    )
    match_score = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_DELIVERY,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Match #{self.id}: Listing {self.listing.id} <-> Order {self.order.id}'
