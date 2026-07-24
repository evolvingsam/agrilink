"""
AI Assistant service — Gemma 4 via Google AI Studio.
Handles the farmer-facing conversational agent:
  - Accepts text (or pre-transcribed text from voice)
  - Builds conversation history context
  - Calls Gemma with a farming-specific system prompt
  - Optionally executes structured actions returned by Gemma
    (e.g. create a produce listing)
"""

import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GOOGLE_AI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

ASSISTANT_SYSTEM_PROMPT = """You are AgriLink Assistant — a helpful agricultural marketplace agent 
serving Nigerian smallholder farmers. You communicate in the farmer's preferred language 
(Hausa, Yoruba, Igbo, Nigerian Pidgin, or English). Always be warm, simple, and practical.

You can help farmers with:
1. Listing produce for sale
2. Checking the status of their listings
3. Understanding market prices
4. Basic agronomy advice (crop care, pest management)

When a farmer wants to list produce, extract the details and return a JSON action block at the end of your response:
<action>{"type": "create_listing", "crop": "<name>", "quantity_kg": <number>, "price_per_kg": <number>, "harvest_date": "<YYYY-MM-DD>"}</action>

If no action is needed, do NOT include an <action> block.
Always respond in the same language the farmer used."""


def _build_history_for_api(messages, use_openrouter=False) -> list:
    """Convert stored Message objects into the format the API expects."""
    history = []
    for msg in messages:
        if use_openrouter:
            role = 'user' if msg.role == 'farmer' else 'assistant'
            history.append({'role': role, 'content': msg.content})
        else:
            role = 'user' if msg.role == 'farmer' else 'model'
            history.append({'role': role, 'parts': [{'text': msg.content}]})
    return history


def _call_gemma_chat(messages_history, new_message: str) -> str:
    """Send conversation history + new message to Gemma, return text reply."""
    api_key = settings.GOOGLE_AI_API_KEY
    use_openrouter = api_key.startswith('sk-or-v1')
    
    history = _build_history_for_api(messages_history, use_openrouter)

    if use_openrouter:
        url = 'https://openrouter.ai/api/v1/chat/completions'
        # Default to a robust Gemma model on OpenRouter if not specified
        model = settings.GOOGLE_AI_MODEL if settings.GOOGLE_AI_MODEL != 'gemma-3-27b-it' else 'google/gemma-4-31b-it'
        
        contents = [{'role': 'system', 'content': ASSISTANT_SYSTEM_PROMPT}] + history + [{'role': 'user', 'content': new_message}]
        
        payload = {
            'model': model,
            'messages': contents,
            'temperature': 0.7,
            'max_tokens': 512,
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    else:
        url = f'{GOOGLE_AI_BASE_URL}/{settings.GOOGLE_AI_MODEL}:generateContent?key={api_key}'
        contents = history + [{'role': 'user', 'parts': [{'text': new_message}]}]
        
        payload = {
            'contents': contents,
            'system_instruction': {
                'parts': [{'text': ASSISTANT_SYSTEM_PROMPT}]
            },
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 512,
            },
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']


def _extract_action(reply_text: str) -> dict | None:
    """Extract optional structured action from Gemma's reply."""
    import re
    match = re.search(r'<action>(.*?)</action>', reply_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            logger.warning('Could not parse action JSON from assistant reply.')
    return None


def _execute_action(action: dict, user) -> dict | None:
    """Execute a structured action returned by Gemma."""
    if action.get('type') == 'create_listing':
        from farmers.models import ProduceListing, CropType

        crop_name = action.get('crop', '').strip()
        try:
            crop_type = CropType.objects.get(name__iexact=crop_name)
        except CropType.DoesNotExist:
            return {'error': f'Unknown crop "{crop_name}". Please ask admin to add it.'}

        from django.utils import timezone
        import datetime
        
        harvest_date_str = action.get('harvest_date')
        try:
            # Try to parse the date to ensure it's valid YYYY-MM-DD
            datetime.date.fromisoformat(harvest_date_str)
            harvest_date = harvest_date_str
        except (ValueError, TypeError):
            # Fallback to today if missing, 'unknown', or invalid format
            harvest_date = timezone.now().date()

        listing = ProduceListing.objects.create(
            farmer=user,
            crop_type=crop_type,
            quantity_kg=action.get('quantity_kg', 0),
            price_per_kg=action.get('price_per_kg', 0),
            harvest_date=harvest_date,
        )
        return {'created_listing_id': listing.id, 'crop': crop_name}

    return None


def chat(conversation, user_message: str, user) -> dict:
    """
    Main entry point for the assistant.
    - Loads conversation history
    - Calls Gemma
    - Saves messages
    - Executes any embedded action
    Returns {'reply': str, 'action_result': dict|None}
    """
    from .models import Message

    if not settings.GOOGLE_AI_API_KEY:
        logger.warning('GOOGLE_AI_API_KEY not set — returning mock assistant response.')
        reply = (
            'Hello! I am AgriLink Assistant. '
            '(Running in mock mode — set GOOGLE_AI_API_KEY to enable real AI responses.) '
            'How can I help you today?'
        )
        Message.objects.create(
            conversation=conversation, role='farmer', content=user_message
        )
        Message.objects.create(
            conversation=conversation, role='assistant', content=reply
        )
        return {'reply': reply, 'action_result': None}

    # Load last 10 message pairs for context (keep API cost low)
    past_messages = conversation.messages.all().order_by('timestamp')[:20]
    history = _build_history_for_api(past_messages)

    try:
        reply = _call_gemma_chat(history, user_message)
    except requests.RequestException as exc:
        logger.error('Gemma API error: %s', exc)
        return {'reply': 'Sorry, I could not connect to the AI service. Please try again.', 'action_result': None}

    # Save both messages
    Message.objects.create(conversation=conversation, role='farmer', content=user_message)
    Message.objects.create(conversation=conversation, role='assistant', content=reply)

    # Extract and execute any action
    action = _extract_action(reply)
    action_result = _execute_action(action, user) if action else None

    return {'reply': reply, 'action_result': action_result}
