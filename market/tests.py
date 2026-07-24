from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from farmers.models import CropType, CollectionPoint
from market.models import MarketPrice
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

class MarketAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.crop1 = CropType.objects.create(name='Tomato')
        self.crop2 = CropType.objects.create(name='Pepper')
        self.hub = CollectionPoint.objects.create(name='Lagos Hub', state='Lagos', lga='Ikeja')

        now = timezone.now().date()
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)

        old_date = fourteen_days_ago + timedelta(days=1)

        # Tomato went up (Old: 1000, New: 1150)
        MarketPrice.objects.create(crop_type=self.crop1, collection_point=self.hub, price_per_kg=Decimal('1000.00'), date=old_date)
        MarketPrice.objects.create(crop_type=self.crop1, collection_point=self.hub, price_per_kg=Decimal('1150.00'), date=now)

        # Pepper went down (Old: 500, New: 400)
        MarketPrice.objects.create(crop_type=self.crop2, collection_point=self.hub, price_per_kg=Decimal('500.00'), date=old_date)
        MarketPrice.objects.create(crop_type=self.crop2, collection_point=self.hub, price_per_kg=Decimal('400.00'), date=now)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='testfarmer', password='password', role='farmer')
        self.client.force_authenticate(user=self.user)

    def test_market_prices_list(self):
        url = reverse('market:prices')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']), 4)

    def test_market_trends(self):
        url = reverse('market:trends')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        
        trends = response.data['data']['trends']
        self.assertEqual(len(trends), 2)
        
        # Trends are sorted by absolute percentage change
        self.assertEqual(trends[0]['crop_name'], 'Pepper')
        self.assertEqual(trends[0]['trend_direction'], 'down')
        self.assertEqual(trends[0]['trend_percentage'], '-20%')
        self.assertEqual(trends[0]['current_avg_price_per_kg'], 400.00)

        self.assertEqual(trends[1]['crop_name'], 'Tomato')
        self.assertEqual(trends[1]['trend_direction'], 'up')
        self.assertEqual(trends[1]['trend_percentage'], '+15%')
        self.assertEqual(trends[1]['current_avg_price_per_kg'], 1150.00)
