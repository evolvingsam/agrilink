from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from .models import MarketPrice
from farmers.models import CropType
import os

try:
    from google import genai as _genai_module
    genai = _genai_module
except ImportError:
    try:
        import google.generativeai as genai
    except ImportError:
        genai = None

def calculate_market_trends(region_id=None):
    """
    Calculates market trends by comparing the average price of crops
    in the last 7 days to the average price in the 7 days before that.
    """
    now = timezone.now().date()
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)

    trends = []
    
    # Query parameters
    # Currently region_id is just an optional filter, could map to CollectionPoint state or LGA.
    # For now, we will just filter by state if region_id is provided and string matches.
    filters = {}
    if region_id:
        filters['collection_point__state__iexact'] = region_id

    crops = CropType.objects.all()
    for crop in crops:
        recent_prices = MarketPrice.objects.filter(
            crop_type=crop,
            date__gt=seven_days_ago,
            date__lte=now,
            **filters
        ).aggregate(avg_price=Avg('price_per_kg'))['avg_price']

        old_prices = MarketPrice.objects.filter(
            crop_type=crop,
            date__gt=fourteen_days_ago,
            date__lte=seven_days_ago,
            **filters
        ).aggregate(avg_price=Avg('price_per_kg'))['avg_price']

        if recent_prices is not None and old_prices is not None and old_prices > 0:
            diff = recent_prices - old_prices
            percentage = (diff / old_prices) * 100
            
            direction = "up" if percentage > 0 else "down" if percentage < 0 else "flat"
            sign = "+" if percentage > 0 else ""
            
            trends.append({
                "crop_name": crop.name,
                "trend_percentage": f"{sign}{percentage:.0f}%",
                "trend_direction": direction,
                "current_avg_price_per_kg": round(recent_prices, 2)
            })
        elif recent_prices is not None:
            # New crop with no old data
            trends.append({
                "crop_name": crop.name,
                "trend_percentage": "+0%",
                "trend_direction": "flat",
                "current_avg_price_per_kg": round(recent_prices, 2)
            })

    # Sort trends by highest percentage change (absolute value) to find top movers
    trends.sort(key=lambda x: abs(float(x["trend_percentage"].replace("%", "").replace("+", ""))), reverse=True)
    
    # Limit to top 5 trends
    top_trends = trends[:5]
    
    summary_alert = _generate_summary_alert(top_trends)
    
    return {
        "summary_alert": summary_alert,
        "trends": top_trends
    }

def _generate_summary_alert(trends):
    """
    Generates a natural language summary of the trends.
    Uses Gemma if available, otherwise a template.
    """
    if not trends:
        return "Market is currently stable. No significant price surges detected."

    up_trends = [t for t in trends if t['trend_direction'] == 'up']
    
    if not up_trends:
        return "Market prices are generally trending downwards or remaining flat."

    top_crops = [t['crop_name'] for t in up_trends[:2]]
    crop_str = " and ".join(top_crops)
    max_surge = max([float(t['trend_percentage'].replace("%", "").replace("+", "")) for t in up_trends])

    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if api_key:
        try:
            import requests as _req
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            prompt = (
                f"Write a 1-2 sentence alert for farmers about market prices. "
                f"Data: {crop_str} are in high demand, prices surged by up to {max_surge}%. "
                f"Keep it professional and encouraging."
            )
            payload = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}]}
            resp = _req.post(url, json=payload, timeout=10)
            if resp.ok:
                return resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception:
            pass  # Fallback to template

    return f"{crop_str} are currently in high demand. Prices have surged by up to {max_surge:.0f}% this week."
