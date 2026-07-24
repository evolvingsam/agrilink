from django.utils import timezone
from .models import Payment
from matching.models import Match
import uuid

def process_mock_payment(match_id: int) -> dict:
    """
    Simulates a payment flow for a match.
    In a real system, this would call an API like Flutterwave.
    Here, we just create a record marking it as completed to show money flow.
    """
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return {'error': 'Match not found'}
        
    if match.status != Match.Status.PENDING_DELIVERY:
        # Assuming we only pay if it hasn't been paid already
        pass # In a real app we'd have better state checks

    # Calculate amount: price_per_kg * quantity_kg
    amount = match.listing.price_per_kg * match.listing.quantity_kg

    payment = Payment.objects.create(
        farmer=match.listing.farmer,
        match=match,
        amount_ngn=amount,
        status=Payment.Status.COMPLETED,
        provider=Payment.Provider.MOCK,
        transaction_ref=f"mock-tx-{uuid.uuid4().hex[:8]}",
        paid_at=timezone.now(),
    )

    # Mark the match as delivered or paid?
    # For demo purposes, we will mark the match as delivered
    match.status = Match.Status.DELIVERED
    match.save(update_fields=['status'])

    # Also mark the buyer order as completed
    match.order.status = match.order.Status.COMPLETED
    match.order.save(update_fields=['status'])

    # Also mark the listing as sold
    match.listing.status = match.listing.Status.SOLD
    match.listing.save(update_fields=['status'])

    return {
        'message': 'Payment processed successfully',
        'payment_id': payment.id,
        'amount': str(amount),
        'transaction_ref': payment.transaction_ref
    }
