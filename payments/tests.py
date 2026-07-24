from django.test import TestCase
from django.contrib.auth import get_user_model
from farmers.models import CropType, CollectionPoint, ProduceListing
from matching.models import BuyerOrder, Match
from payments.models import Payment
from payments.service import process_mock_payment
from decimal import Decimal

User = get_user_model()

class PaymentServiceTests(TestCase):
    def setUp(self):
        self.farmer_user = User.objects.create_user(username='farmer', role='farmer', password='password')
        self.buyer_user = User.objects.create_user(username='buyer', role='buyer', password='password')
        
        # In accounts.models, BuyerProfile is created by signal when role='buyer'
        # Or we might need to make sure BuyerProfile exists. But we just access buyer_user.buyer_profile
        
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

    def test_process_mock_payment_success(self):
        result = process_mock_payment(self.match.id)
        
        self.assertIn('payment_id', result)
        self.assertEqual(Decimal(result['amount']), Decimal('50000.00'))
        
        payment = Payment.objects.get(id=result['payment_id'])
        self.assertEqual(payment.amount_ngn, Decimal('50000.00'))
        self.assertEqual(payment.status, Payment.Status.COMPLETED)
        
        # Check if statuses were updated
        self.match.refresh_from_db()
        self.order.refresh_from_db()
        self.listing.refresh_from_db()
        
        self.assertEqual(self.match.status, Match.Status.DELIVERED)
        self.assertEqual(self.order.status, BuyerOrder.Status.COMPLETED)
        self.assertEqual(self.listing.status, ProduceListing.Status.SOLD)

    def test_process_mock_payment_not_found(self):
        result = process_mock_payment(9999)
        self.assertIn('error', result)
