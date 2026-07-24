from django.test import TestCase
from django.contrib.auth import get_user_model
from farmers.models import CropType, CollectionPoint, ProduceListing
from accounts.models import BuyerProfile
from matching.models import BuyerOrder, Match
from logistics.models import DispatchRoute
from logistics.service import create_data_model, generate_routes
from decimal import Decimal

User = get_user_model()

class LogisticsServiceTests(TestCase):
    def setUp(self):
        self.farmer_user = User.objects.create_user(username='farmer', role='farmer', password='password')
        self.buyer_user = User.objects.create_user(username='buyer', role='buyer', password='password')
        
        # Create buyer_profile with coordinates
        bp = BuyerProfile.objects.create(user=self.buyer_user)
        bp.latitude = Decimal('12.0001')
        bp.longitude = Decimal('8.0001')
        bp.save()
        
        self.crop = CropType.objects.create(name='Tomato')
        self.cp = CollectionPoint.objects.create(name='Kano Hub', latitude=12.0, longitude=8.0)
        
        self.listing = ProduceListing.objects.create(
            farmer=self.farmer_user,
            crop_type=self.crop,
            collection_point=self.cp,
            quantity_kg=Decimal('100.00'),
            price_per_kg=Decimal('500.00'),
            status=ProduceListing.Status.GRADED,
            harvest_date='2026-07-20'
        )
        
        self.order = BuyerOrder.objects.create(
            buyer=self.buyer_user,
            crop_type=self.crop,
            quantity_kg=Decimal('100.00'),
            max_price_per_kg=Decimal('600.00'),
            status=BuyerOrder.Status.OPEN
        )
        
        self.match = Match.objects.create(
            order=self.order,
            listing=self.listing,
            status=Match.Status.PENDING_DELIVERY
        )

    def test_create_data_model(self):
        matches = [self.match]
        data = create_data_model(matches)
        
        self.assertIn('locations', data)
        self.assertIn('distance_matrix', data)
        self.assertIn('pickups_deliveries', data)
        self.assertEqual(len(data['locations']), 3) # Depot + Pickup + Delivery
        self.assertEqual(len(data['distance_matrix']), 3)

    def test_generate_routes(self):
        # generate_routes modifies DB and uses Google API. 
        # We will test if it creates a route when pending matches exist.
        # Since we use Mock for Gemma in our service when key is absent, it should run locally cleanly.
        routes_created = generate_routes()
        self.assertEqual(routes_created, 1)
        
        route = DispatchRoute.objects.first()
        self.assertIsNotNone(route)
        self.assertEqual(route.status, DispatchRoute.Status.PLANNED)
        self.assertEqual(route.matches.count(), 1)
        self.assertIn(self.match, route.matches.all())
