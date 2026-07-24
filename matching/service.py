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
            # Find eligible listings (same crop, graded or ungraded, quantity >= order.quantity_kg)
            # For simplicity, we match a single listing that can fulfill the order.
            # In a real app, we might match multiple listings to fulfill one order.
            eligible_listings = ProduceListing.objects.filter(
                status__in=[ProduceListing.Status.PENDING, ProduceListing.Status.GRADED],
                crop_type=order.crop_type,
                quantity_kg__gte=order.quantity_kg,
                quality_grade__in=[order.required_grade, ProduceListing.Grade.A] # Just an example, accept requested or better
            ).order_by('price_per_kg')

            if eligible_listings.exists():
                best_listing = eligible_listings.first()
                
                # Create match
                Match.objects.create(
                    listing=best_listing,
                    order=order,
                    match_score=100.0, # Mock score
                )
                
                # Update statuses
                best_listing.status = ProduceListing.Status.MATCHED
                best_listing.save(update_fields=['status'])
                
                order.status = BuyerOrder.Status.MATCHED
                order.save(update_fields=['status'])
                
                matches_created += 1

    return matches_created
