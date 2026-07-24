from django.db import models
from django.conf import settings


class CropType(models.Model):
    """Reference table for crop types."""
    name = models.CharField(max_length=100, unique=True)
    typical_shelf_life_days = models.PositiveIntegerField(default=7)
    perishability_score = models.PositiveSmallIntegerField(
        default=5,
        help_text='1 (least) to 10 (most perishable)',
    )

    def __str__(self):
        return self.name


class CollectionPoint(models.Model):
    """Physical aggregation point where farmers drop off produce."""
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    has_cold_storage = models.BooleanField(default=False)
    solar_powered = models.BooleanField(default=False)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.state})'


class ProduceListing(models.Model):
    """A farmer's listing of produce available for sale."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Grading'
        GRADED = 'graded', 'Graded'
        MATCHED = 'matched', 'Matched to Buyer'
        SOLD = 'sold', 'Sold'
        EXPIRED = 'expired', 'Expired'

    class Grade(models.TextChoices):
        A = 'A', 'Grade A (Premium)'
        B = 'B', 'Grade B (Standard)'
        C = 'C', 'Grade C (Below Standard)'
        REJECTED = 'rejected', 'Rejected'
        UNGRADED = 'ungraded', 'Not Yet Graded'

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        limit_choices_to={'role': 'farmer'},
    )
    crop_type = models.ForeignKey(
        CropType,
        on_delete=models.PROTECT,
        related_name='listings',
    )
    collection_point = models.ForeignKey(
        CollectionPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listings',
    )
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    harvest_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    quality_grade = models.CharField(
        max_length=10,
        choices=Grade.choices,
        default=Grade.UNGRADED,
    )
    photo = models.ImageField(
        upload_to='produce/photos/',
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.farmer.username} — {self.crop_type.name} ({self.quantity_kg}kg)'
