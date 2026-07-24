from django.db import models
from django.conf import settings
from matching.models import Match


class Payment(models.Model):
    """A payment record for a matched and delivered produce order."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class Provider(models.TextChoices):
        FLUTTERWAVE = 'flutterwave', 'Flutterwave'
        PAYSTACK = 'paystack', 'Paystack'
        MOCK = 'mock', 'Mock/Wallet'

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments',
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.PROTECT,
        related_name='payments',
    )
    amount_ngn = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    transaction_ref = models.CharField(max_length=100, blank=True)
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.MOCK,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment {self.id} for Match {self.match.id} - {self.status}'
