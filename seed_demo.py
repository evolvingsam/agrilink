"""
AgriLink Demo Seed Script — run with: py manage.py shell < seed_demo.py
Seeds the Render PostgreSQL database with realistic Nigerian agricultural data.
"""
from decimal import Decimal
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import date, timedelta

# ──────────────────────────────────────────────
# 1. ACCOUNTS
# ──────────────────────────────────────────────
from accounts.models import User, FarmerProfile, BuyerProfile

# Buyer — godsown
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
print("✅ Buyer godsown seeded")

# Farmer — mrv_farmer
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
    'latitude': Decimal('7.3775'),
    'longitude': Decimal('3.9470'),
})
print("✅ Farmer mrv_farmer seeded")

# Extra farmer account for variety
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
    'latitude': Decimal('6.2104'),
    'longitude': Decimal('7.0669'),
})
print("✅ Farmer emeka_farm seeded")

# Dispatcher account
dispatcher, _ = User.objects.get_or_create(username='dispatch_lagos')
dispatcher.set_password('mikky123')
dispatcher.role = 'dispatcher'
dispatcher.first_name = 'Ibrahim'
dispatcher.last_name = 'Musa'
dispatcher.email = 'ibrahim@agrilink.ng'
dispatcher.phone = '+2348077788899'
dispatcher.save()
print("✅ Dispatcher dispatch_lagos seeded")

# ──────────────────────────────────────────────
# 2. CROP TYPES
# ──────────────────────────────────────────────
from farmers.models import CropType, CollectionPoint, ProduceListing

crops_data = [
    {'name': 'Tomato',       'perishability_score': 8, 'typical_shelf_life_days': 7},
    {'name': 'Pepper',       'perishability_score': 7, 'typical_shelf_life_days': 10},
    {'name': 'Yam',          'perishability_score': 3, 'typical_shelf_life_days': 60},
    {'name': 'Cassava',      'perishability_score': 4, 'typical_shelf_life_days': 30},
    {'name': 'Maize',        'perishability_score': 2, 'typical_shelf_life_days': 90},
    {'name': 'Plantain',     'perishability_score': 7, 'typical_shelf_life_days': 8},
    {'name': 'Sweet Potato', 'perishability_score': 4, 'typical_shelf_life_days': 45},
    {'name': 'Okra',         'perishability_score': 9, 'typical_shelf_life_days': 4},
    {'name': 'Watermelon',   'perishability_score': 5, 'typical_shelf_life_days': 14},
    {'name': 'Ginger',       'perishability_score': 2, 'typical_shelf_life_days': 120},
]
crop_objects = {}
for c in crops_data:
    obj, _ = CropType.objects.get_or_create(name=c['name'], defaults={
        'perishability_score': c['perishability_score'],
        'typical_shelf_life_days': c['typical_shelf_life_days'],
    })
    crop_objects[c['name']] = obj
print(f"✅ {len(crop_objects)} crop types seeded")

# ──────────────────────────────────────────────
# 3. COLLECTION POINTS
# ──────────────────────────────────────────────
cps_data = [
    {'name': 'Mile 12 Market Hub',   'state': 'Lagos',    'lga': 'Kosofe',       'lat': 6.6009, 'lng': 3.3908},
    {'name': 'Bodija Agric Centre',  'state': 'Oyo',      'lga': 'Ibadan North', 'lat': 7.4167, 'lng': 3.9000},
    {'name': 'Kano North Gate Hub',  'state': 'Kano',     'lga': 'Kano Municipal','lat': 12.005, 'lng': 8.5920},
    {'name': 'Onitsha Trade Point',  'state': 'Anambra',  'lga': 'Onitsha North','lat': 6.1429, 'lng': 6.7871},
    {'name': 'Gboko Agric Hub',      'state': 'Benue',    'lga': 'Gboko',        'lat': 7.3189, 'lng': 9.0004},
]
cp_objects = {}
for cp in cps_data:
    obj, _ = CollectionPoint.objects.get_or_create(name=cp['name'], defaults={
        'state': cp['state'],
        'lga': cp['lga'],
        'latitude': Decimal(str(cp['lat'])),
        'longitude': Decimal(str(cp['lng'])),
    })
    cp_objects[cp['name']] = obj
print(f"✅ {len(cp_objects)} collection points seeded")

# ──────────────────────────────────────────────
# 4. PRODUCE LISTINGS
# ──────────────────────────────────────────────
listings_data = [
    {'farmer': farmer,  'crop': 'Tomato',   'qty': 500, 'price': 450,  'grade': 'A', 'status': 'graded', 'cp': 'Bodija Agric Centre',  'harvest_days_ago': 2},
    {'farmer': farmer,  'crop': 'Pepper',   'qty': 300, 'price': 600,  'grade': 'A', 'status': 'graded', 'cp': 'Bodija Agric Centre',  'harvest_days_ago': 1},
    {'farmer': farmer,  'crop': 'Plantain', 'qty': 200, 'price': 300,  'grade': 'B', 'status': 'graded', 'cp': 'Bodija Agric Centre',  'harvest_days_ago': 3},
    {'farmer': farmer2, 'crop': 'Yam',      'qty': 800, 'price': 350,  'grade': 'A', 'status': 'graded', 'cp': 'Onitsha Trade Point',  'harvest_days_ago': 5},
    {'farmer': farmer2, 'crop': 'Cassava',  'qty': 600, 'price': 150,  'grade': 'A', 'status': 'graded', 'cp': 'Onitsha Trade Point',  'harvest_days_ago': 4},
    {'farmer': farmer2, 'crop': 'Okra',     'qty': 100, 'price': 800,  'grade': 'A', 'status': 'graded', 'cp': 'Onitsha Trade Point',  'harvest_days_ago': 1},
    {'farmer': farmer,  'crop': 'Maize',    'qty': 1000,'price': 200,  'grade': 'B', 'status': 'pending','cp': 'Gboko Agric Hub',       'harvest_days_ago': 10},
    {'farmer': farmer2, 'crop': 'Ginger',   'qty': 150, 'price': 1200, 'grade': 'A', 'status': 'graded', 'cp': 'Kano North Gate Hub',  'harvest_days_ago': 7},
    {'farmer': farmer,  'crop': 'Sweet Potato','qty':400,'price': 250, 'grade': 'B', 'status': 'graded', 'cp': 'Bodija Agric Centre',  'harvest_days_ago': 3},
    {'farmer': farmer2, 'crop': 'Watermelon','qty': 250, 'price': 180,  'grade': 'A', 'status': 'graded', 'cp': 'Mile 12 Market Hub',  'harvest_days_ago': 2},
]
for l in listings_data:
    ProduceListing.objects.get_or_create(
        farmer=l['farmer'],
        crop_type=crop_objects[l['crop']],
        collection_point=cp_objects[l['cp']],
        defaults={
            'quantity_kg': Decimal(str(l['qty'])),
            'price_per_kg': Decimal(str(l['price'])),
            'quality_grade': l['grade'],
            'status': l['status'],
            'harvest_date': date.today() - timedelta(days=l['harvest_days_ago']),
        }
    )
print(f"✅ {len(listings_data)} produce listings seeded")

# ──────────────────────────────────────────────
# 5. MARKET PRICES (last 14 days of history)
# ──────────────────────────────────────────────
from market.models import MarketPrice

market_prices = [
    ('Tomato', 420, 460, 480, 500, 510, 490, 470),
    ('Pepper', 550, 580, 600, 610, 590, 570, 560),
    ('Yam',    320, 330, 340, 355, 350, 345, 340),
    ('Maize',  180, 185, 195, 200, 205, 210, 200),
    ('Okra',   750, 780, 800, 820, 810, 790, 780),
]

for crop_name, *prices in market_prices:
    crop = crop_objects.get(crop_name)
    if not crop:
        continue
    for i, price in enumerate(prices):
        entry_date = date.today() - timedelta(days=len(prices) - i)
        for cp in list(cp_objects.values())[:3]:
            MarketPrice.objects.get_or_create(
                crop_type=crop,
                collection_point=cp,
                date=entry_date,
                defaults={'price_per_kg': Decimal(str(price + (hash(cp.name) % 50)))}
            )
print("✅ Market price history seeded")

# ──────────────────────────────────────────────
# 6. BUYER ORDERS (from godsown)
# ──────────────────────────────────────────────
from matching.models import BuyerOrder

orders_data = [
    {'crop': 'Tomato',    'qty': 100, 'max_price': 9000,  'grade': 'A', 'status': 'waiting_for_payment'},
    {'crop': 'Pepper',    'qty': 50,  'max_price': 10000, 'grade': 'A', 'status': 'open'},
    {'crop': 'Yam',       'qty': 200, 'max_price': 5000,  'grade': 'A', 'status': 'open'},
]
for o in orders_data:
    BuyerOrder.objects.get_or_create(
        buyer=buyer,
        crop_type=crop_objects[o['crop']],
        defaults={
            'quantity_kg': Decimal(str(o['qty'])),
            'max_price_per_kg': Decimal(str(o['max_price'])),
            'required_grade': o['grade'],
            'status': o['status'],
        }
    )
print(f"✅ {len(orders_data)} buyer orders seeded")

print("\n🌾 Demo database seeded successfully!")
print("   Buyer:      godsown / mikky123")
print("   Farmer:     mrv_farmer / mikky123")
print("   Farmer 2:   emeka_farm / mikky123")
print("   Dispatcher: dispatch_lagos / mikky123")
