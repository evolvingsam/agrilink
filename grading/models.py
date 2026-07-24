from django.db import models
from farmers.models import ProduceListing


class GradingResult(models.Model):
    """Stores the AI quality grading result for a produce listing."""

    listing = models.OneToOneField(
        ProduceListing,
        on_delete=models.CASCADE,
        related_name='grading_result',
    )
    grade = models.CharField(max_length=10)
    issues = models.JSONField(default=list, blank=True)
    estimated_shelf_days = models.PositiveIntegerField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    raw_response = models.TextField(blank=True, help_text='Full Gemma response for debugging')
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Grade {self.grade} for listing #{self.listing_id}'
