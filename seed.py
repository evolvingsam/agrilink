"""
Seed script — populate initial CropType data.
Run: python manage.py shell < seed.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrilink.settings')
django.setup()

from farmers.models import CropType

crops = [
    {'name': 'Tomato',   'typical_shelf_life_days': 7,  'perishability_score': 9},
    {'name': 'Cassava',  'typical_shelf_life_days': 14, 'perishability_score': 4},
    {'name': 'Yam',      'typical_shelf_life_days': 30, 'perishability_score': 3},
    {'name': 'Maize',    'typical_shelf_life_days': 21, 'perishability_score': 4},
    {'name': 'Plantain', 'typical_shelf_life_days': 5,  'perishability_score': 8},
    {'name': 'Pepper',   'typical_shelf_life_days': 10, 'perishability_score': 7},
    {'name': 'Onion',    'typical_shelf_life_days': 30, 'perishability_score': 4},
    {'name': 'Groundnut','typical_shelf_life_days': 60, 'perishability_score': 2},
]

for crop in crops:
    obj, created = CropType.objects.get_or_create(name=crop['name'], defaults=crop)
    print(f"{'Created' if created else 'Exists '} → {obj.name}")

print('\nDone.')
