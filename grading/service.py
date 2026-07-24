"""
Grading service — sends produce photo + metadata to Gemma 4 via
Google AI Studio and returns a structured quality assessment.
"""

import json
import base64
import logging
import requests
from django.conf import settings
from farmers.models import ProduceListing
from .models import GradingResult

logger = logging.getLogger(__name__)

GOOGLE_AI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

GRADING_SYSTEM_PROMPT = """You are an expert agricultural quality inspector for Nigerian produce markets.
Analyze the provided image and return ONLY valid JSON with no extra text, using exactly these fields:
{
  "grade": "A" | "B" | "C" | "rejected",
  "issues": ["list", "of", "observed", "defects"],
  "estimated_shelf_days": <integer>,
  "confidence": <float between 0.0 and 1.0>
}

Grade definitions:
- A: Premium quality, minimal defects, suitable for high-end markets
- B: Standard quality, minor blemishes, suitable for general market
- C: Below standard, visible damage/disease, suitable for processing only
- rejected: Severe spoilage or contamination, not fit for sale
"""


def _encode_image_to_base64(image_file) -> str:
    """Read an uploaded image file and return base64-encoded string."""
    image_file.seek(0)
    return base64.b64encode(image_file.read()).decode('utf-8')


def _call_gemma_vision(image_b64: str, mime_type: str, crop_name: str) -> dict:
    """
    Call Google AI Studio or OpenRouter with image + text prompt.
    Returns parsed JSON dict from Gemma's response.
    """
    api_key = settings.GOOGLE_AI_API_KEY
    use_openrouter = api_key.startswith('sk-or-v1')
    
    prompt_text = f'Inspect this {crop_name} produce image. Return JSON quality assessment only.'

    if use_openrouter:
        url = 'https://openrouter.ai/api/v1/chat/completions'
        # Default to a robust vision model on OpenRouter
        model = 'google/gemma-4-31b-it'
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': GRADING_SYSTEM_PROMPT},
                {
                    'role': 'user', 
                    'content': [
                        {'type': 'text', 'text': prompt_text},
                        {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{image_b64}'}}
                    ]
                }
            ],
            'temperature': 0.1,
            'max_tokens': 200,
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        response.raise_for_status()
        raw_text = response.json()['choices'][0]['message']['content']
        
        # Strip markdown json blocks if OpenRouter model returned them
        if raw_text.startswith('```json'):
            raw_text = raw_text.replace('```json\n', '').replace('\n```', '')
            
        return json.loads(raw_text), raw_text

    else:
        model = settings.GOOGLE_AI_MODEL
        url = f'{GOOGLE_AI_BASE_URL}/{model}:generateContent?key={api_key}'

        payload = {
            'contents': [
                {
                    'parts': [
                        {
                            'inline_data': {
                                'mime_type': mime_type,
                                'data': image_b64,
                            }
                        },
                        {
                            'text': prompt_text
                        },
                    ]
                }
            ],
            'system_instruction': {
                'parts': [{'text': GRADING_SYSTEM_PROMPT}]
            },
            'generationConfig': {
                'temperature': 0.1,
                'responseMimeType': 'application/json',
            },
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract text from Gemma's response
        raw_text = data['candidates'][0]['content']['parts'][0]['text']
        return json.loads(raw_text), raw_text


def run_grading(listing: ProduceListing) -> dict:
    """
    Main entry point — grades a produce listing's photo.
    Updates ProduceListing.quality_grade and creates/updates GradingResult.
    Returns the grading result dict.
    """
    if not listing.photo:
        return {'error': 'No photo attached to this listing.'}

    if not settings.GOOGLE_AI_API_KEY:
        logger.warning('GOOGLE_AI_API_KEY not set — skipping real grading, returning mock.')
        return _mock_grading(listing)

    try:
        # Determine MIME type from file extension
        photo_name = listing.photo.name.lower()
        if photo_name.endswith('.png'):
            mime_type = 'image/png'
        elif photo_name.endswith('.webp'):
            mime_type = 'image/webp'
        else:
            mime_type = 'image/jpeg'

        image_b64 = _encode_image_to_base64(listing.photo)
        result, raw_text = _call_gemma_vision(image_b64, mime_type, listing.crop_type.name)

        grade = result.get('grade', 'B')
        issues = result.get('issues', [])
        shelf_days = result.get('estimated_shelf_days')
        confidence = result.get('confidence')

    except (requests.RequestException, json.JSONDecodeError, KeyError) as exc:
        logger.error('Grading API error for listing %s: %s', listing.id, exc)
        return {'error': str(exc)}

    # Persist result
    GradingResult.objects.update_or_create(
        listing=listing,
        defaults={
            'grade': grade,
            'issues': issues,
            'estimated_shelf_days': shelf_days,
            'confidence': confidence,
            'raw_response': raw_text,
        },
    )

    # Update the listing status and grade
    listing.quality_grade = grade
    listing.status = ProduceListing.Status.GRADED
    listing.save(update_fields=['quality_grade', 'status', 'updated_at'])

    return {
        'grade': grade,
        'issues': issues,
        'estimated_shelf_days': shelf_days,
        'confidence': confidence,
    }


def _mock_grading(listing: ProduceListing) -> dict:
    """
    Returns a mock grading result when no API key is configured.
    Useful for local development without spending API credits.
    """
    mock = {
        'grade': 'A',
        'issues': [],
        'estimated_shelf_days': listing.crop_type.typical_shelf_life_days,
        'confidence': 0.95,
    }

    GradingResult.objects.update_or_create(
        listing=listing,
        defaults={
            **mock,
            'raw_response': '{"mock": true}',
        },
    )
    listing.quality_grade = 'A'
    listing.status = ProduceListing.Status.GRADED
    listing.save(update_fields=['quality_grade', 'status', 'updated_at'])

    return mock
