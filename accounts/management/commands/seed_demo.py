from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed the database with AgriLink demo data'

    def handle(self, *args, **kwargs):
        from accounts.models import User, FarmerProfile, BuyerProfile
        from farmers.models import CropType, CollectionPoint, ProduceListing
        from matching.models import BuyerOrder
        from market.models import MarketPrice

        # ── ACCOUNTS ──────────────────────────────────────────────────
        buyer, _ = User.objects.get_or_create(username='godsown')
        buyer.set_password('mikky123')
        buyer.role = 'buyer'
        buyer.first_name = 'Godsown'
        buyer.last_name = 'Alawode'
        buyer.email = 'godsown@agrilink.ng'
        buyer.phone = '+2348012345678'
        buyer.wallet_balance = Decimal('500000.00')
        buyer.save()
        BuyerProfile.objects.update_or_create(user=buyer, defaults={
            'business_name': 'Godsown Fresh Produce Ltd',
            'location': 'Ikeja, Lagos',
            'verified_status': True,
            'latitude': Decimal('6.6018'),
            'longitude': Decimal('3.3515'),
        })
        self.stdout.write(self.style.SUCCESS('Buyer godsown seeded'))

        farmer, _ = User.objects.get_or_create(username='mrv_farmer')
        farmer.set_password('mikky123')
        farmer.role = 'farmer'
        farmer.first_name = 'Marvellous'
        farmer.last_name = 'Adeyemi'
        farmer.email = 'mrv@agrilink.ng'
        farmer.phone = '+2348098765432'
        farmer.wallet_balance = Decimal('75000.00')
        farmer.save()
        FarmerProfile.objects.update_or_create(user=farmer, defaults={
            'state': 'Oyo',
            'lga': 'Ibadan North',
            'preferred_language': 'yo',
            'farm_size_hectares': Decimal('12.50'),
        })
        self.stdout.write(self.style.SUCCESS('Farmer mrv_farmer seeded'))

        farmer2, _ = User.objects.get_or_create(username='emeka_farm')
        farmer2.set_password('mikky123')
        farmer2.role = 'farmer'
        farmer2.first_name = 'Emeka'
        farmer2.last_name = 'Okonkwo'
        farmer2.email = 'emeka@agrilink.ng'
        farmer2.phone = '+2348055544433'
        farmer2.wallet_balance = Decimal('42000.00')
        farmer2.save()
        FarmerProfile.objects.update_or_create(user=farmer2, defaults={
            'state': 'Anambra',
            'lga': 'Awka South',
            'preferred_language': 'ig',
            'farm_size_hectares': Decimal('8.00'),
        })
        self.stdout.write(self.style.SUCCESS('Farmer emeka_farm seeded'))

        dispatcher, _ = User.objects.get_or_create(username='dispatch_lagos')
        dispatcher.set_password('mikky123')
        dispatcher.role = 'dispatcher'
        dispatcher.first_name = 'Ibrahim'
        dispatcher.last_name = 'Musa'
        dispatcher.email = 'ibrahim@agrilink.ng'
        dispatcher.phone = '+2348077788899'
        dispatcher.save()
        self.stdout.write(self.style.SUCCESS('Dispatcher dispatch_lagos seeded'))

        # ── CROP TYPES ────────────────────────────────────────────────
        crops_data = [
            ('Tomato', 8, 7), ('Pepper', 7, 10), ('Yam', 3, 60),
            ('Cassava', 4, 30), ('Maize', 2, 90), ('Plantain', 7, 8),
            ('Sweet Potato', 4, 45), ('Okra', 9, 4),
            ('Watermelon', 5, 14), ('Ginger', 2, 120),
        ]
        crop_objects = {}
        for name, perishability, shelf_life in crops_data:
            obj, _ = CropType.objects.get_or_create(name=name, defaults={
                'perishability_score': perishability,
                'typical_shelf_life_days': shelf_life,
            })
            crop_objects[name] = obj
        self.stdout.write(self.style.SUCCESS(f'{len(crop_objects)} crop types seeded'))

        # ── COLLECTION POINTS ─────────────────────────────────────────
        cps_data = [
            ('Mile 12 Market Hub', 'Lagos', 'Kosofe', '6.6009', '3.3908'),
            ('Bodija Agric Centre', 'Oyo', 'Ibadan North', '7.4167', '3.9000'),
            ('Kano North Gate Hub', 'Kano', 'Kano Municipal', '12.005', '8.5920'),
            ('Onitsha Trade Point', 'Anambra', 'Onitsha North', '6.1429', '6.7871'),
            ('Gboko Agric Hub', 'Benue', 'Gboko', '7.3189', '9.0004'),
        ]
        cp_objects = {}
        for name, state, lga, lat, lng in cps_data:
            obj, _ = CollectionPoint.objects.get_or_create(name=name, defaults={
                'state': state, 'lga': lga,
                'latitude': Decimal(lat), 'longitude': Decimal(lng),
            })
            cp_objects[name] = obj
        self.stdout.write(self.style.SUCCESS(f'{len(cp_objects)} collection points seeded'))

        # ── PRODUCE LISTINGS ──────────────────────────────────────────
        listings_data = [
            (farmer, 'Tomato', 500, 450, 'A', 'graded', 'Bodija Agric Centre', 2),
            (farmer, 'Pepper', 300, 600, 'A', 'graded', 'Bodija Agric Centre', 1),
            (farmer, 'Plantain', 200, 300, 'B', 'graded', 'Bodija Agric Centre', 3),
            (farmer2, 'Yam', 800, 350, 'A', 'graded', 'Onitsha Trade Point', 5),
            (farmer2, 'Cassava', 600, 150, 'A', 'graded', 'Onitsha Trade Point', 4),
            (farmer2, 'Okra', 100, 800, 'A', 'graded', 'Onitsha Trade Point', 1),
            (farmer, 'Maize', 1000, 200, 'B', 'graded', 'Gboko Agric Hub', 10),
            (farmer2, 'Ginger', 150, 1200, 'A', 'graded', 'Kano North Gate Hub', 7),
            (farmer, 'Sweet Potato', 400, 250, 'B', 'graded', 'Bodija Agric Centre', 3),
            (farmer2, 'Watermelon', 250, 180, 'A', 'graded', 'Mile 12 Market Hub', 2),
        ]
        created = 0
        for f, crop, qty, price, grade, status, cp, days_ago in listings_data:
            _, is_new = ProduceListing.objects.get_or_create(
                farmer=f,
                crop_type=crop_objects[crop],
                collection_point=cp_objects[cp],
                quality_grade=grade,
                defaults={
                    'quantity_kg': Decimal(str(qty)),
                    'price_per_kg': Decimal(str(price)),
                    'status': status,
                    'harvest_date': date.today() - timedelta(days=days_ago),
                }
            )
            if is_new:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} produce listings seeded'))

        # ── MARKET PRICES ─────────────────────────────────────────────
        price_history = {
            'Tomato':   [420, 440, 460, 480, 490, 500, 510, 495, 480, 470, 460, 450, 460, 470],
            'Pepper':   [550, 560, 575, 580, 590, 600, 610, 605, 595, 585, 570, 560, 555, 565],
            'Yam':      [320, 325, 330, 338, 340, 350, 355, 350, 345, 340, 338, 335, 330, 332],
            'Maize':    [180, 182, 185, 190, 195, 200, 205, 210, 208, 205, 200, 198, 195, 193],
            'Okra':     [750, 760, 775, 780, 800, 810, 820, 815, 808, 800, 795, 790, 785, 780],
        }
        mp_count = 0
        cp_list = list(cp_objects.values())[:3]
        for crop_name, prices in price_history.items():
            crop = crop_objects.get(crop_name)
            if not crop:
                continue
            for i, price in enumerate(prices):
                entry_date = date.today() - timedelta(days=len(prices) - i)
                for cp in cp_list:
                    _, is_new = MarketPrice.objects.get_or_create(
                        crop_type=crop, collection_point=cp, date=entry_date,
                        defaults={'price_per_kg': Decimal(str(price))}
                    )
                    if is_new:
                        mp_count += 1
        self.stdout.write(self.style.SUCCESS(f'{mp_count} market price records seeded'))

        # ── BUYER ORDERS ──────────────────────────────────────────────
        orders_data = [
            ('Tomato', 100, 9000, 'A', 'waiting_for_payment'),
            ('Pepper', 50, 10000, 'A', 'open'),
            ('Yam', 200, 5000, 'A', 'open'),
            ('Okra', 30, 15000, 'A', 'open'),
        ]
        for crop, qty, max_price, grade, status in orders_data:
            BuyerOrder.objects.get_or_create(
                buyer=buyer,
                crop_type=crop_objects[crop],
                defaults={
                    'quantity_kg': Decimal(str(qty)),
                    'max_price_per_kg': Decimal(str(max_price)),
                    'required_grade': grade,
                    'status': status,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'{len(orders_data)} buyer orders seeded'))

        self.stdout.write(self.style.SUCCESS('\nDemo database seeded successfully!'))
        self.stdout.write('  Accounts:   godsown / mrv_farmer / emeka_farm / dispatch_lagos')
        self.stdout.write('  Password:   mikky123 for all accounts')
