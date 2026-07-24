from django.db import models
from farmers.models import CropType, CollectionPoint

class MarketPrice(models.Model):
    """Historical or current market price for a crop at a specific collection point."""
    crop_type = models.ForeignKey(
        CropType,
        on_delete=models.CASCADE,
        related_name='market_prices',
    )
    collection_point = models.ForeignKey(
        CollectionPoint,
        on_delete=models.CASCADE,
        related_name='market_prices',
    )
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ('crop_type', 'collection_point', 'date')

    def __str__(self):
        return f'{self.crop_type.name} @ {self.collection_point.name} - {self.price_per_kg} NGN on {self.date}'
