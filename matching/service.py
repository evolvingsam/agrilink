from django.db import transaction
from .models import BuyerOrder, Match
from farmers.models import ProduceListing

def run_matching_cycle() -> int:
    """
    Finds unmatched BuyerOrders and matches them with available ProduceListings.
    Returns the number of matches created.
    """
    matches_created = 0

    open_orders = BuyerOrder.objects.filter(status=BuyerOrder.Status.OPEN)

    for order in open_orders:
        with transaction.atomic():
            # Find eligible listings (same crop, graded or ungraded, quantity >= order.quantity_kg, price <= max_price)
            eligible_listings = ProduceListing.objects.filter(
                status__in=[ProduceListing.Status.PENDING, ProduceListing.Status.GRADED],
                crop_type=order.crop_type,
                quantity_kg__gte=order.quantity_kg,
                price_per_kg__lte=order.max_price_per_kg,
                quality_grade__in=[order.required_grade, ProduceListing.Grade.A, ProduceListing.Grade.UNGRADED]
            ).order_by('price_per_kg')

            if eligible_listings.exists():
                best_listing = eligible_listings.first()
                
                # Create match
                Match.objects.create(
                    listing=best_listing,
                    order=order,
                    match_score=100.0, # Mock score
                )
                
                # Update listing status to MATCHED
                best_listing.status = ProduceListing.Status.MATCHED
                best_listing.save(update_fields=['status'])

                # Advance the order to waiting_for_payment so the buyer can pay
                order.status = BuyerOrder.Status.WAITING_FOR_PAYMENT
                order.save(update_fields=['status'])
                
                matches_created += 1

    return matches_created
