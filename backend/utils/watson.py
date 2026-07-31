"""
AURA AI - IBM Watson Integration
NLP, Assistant, and Visual Recognition services
"""

import os
import json
import logging
import random
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

WATSON_MODE = os.getenv('WATSON_MODE', 'mock')
WATSON_API_KEY = os.getenv('WATSON_API_KEY', '')
WATSON_URL = os.getenv('WATSON_URL', '')
WATSON_ASSISTANT_ID = os.getenv('WATSON_ASSISTANT_ID', '')
WATSON_PROJECT_ID = os.getenv('WATSON_PROJECT_ID', '')


def _is_live():
    return WATSON_MODE == 'live' and WATSON_API_KEY and WATSON_URL


# ─── Watson NLP: Prompt Analysis ─────────────────────────────────

def analyze_prompt(prompt):
    """Analyze a creative prompt using Watson NLP."""
    if _is_live():
        return _analyze_prompt_live(prompt)
    return _analyze_prompt_mock(prompt)


def _analyze_prompt_mock(prompt):
    words = prompt.lower().split()
    word_count = len(words)
    char_count = len(prompt)

    sentiment_keywords = {
        'positive': ['beautiful', 'amazing', 'stunning', 'gorgeous', 'elegant', 'luxury', 'vibrant', 'bright', 'warm', 'happy', 'peaceful', 'dreamy', 'romantic', 'magical', 'serene'],
        'negative': ['dark', 'gloomy', 'scary', 'sad', 'gritty', 'decay', 'wasteland', 'apocalyptic', 'chaos', 'bleak', 'abandoned'],
        'artistic': ['abstract', 'surreal', 'minimal', 'geometric', 'vintage', 'retro', 'cinematic', 'dramatic', 'ethereal', 'whimsical']
    }

    scores = {'positive': 0, 'negative': 0, 'artistic': 0}
    for w in words:
        for cat, kw_list in sentiment_keywords.items():
            if w in kw_list:
                scores[cat] += 1

    total = sum(scores.values()) or 1
    sentiment = max(scores, key=scores.get)

    style_keywords = {
        'realistic': ['photorealistic', 'realistic', 'photo', 'photography', '8k', 'detailed', 'canon', 'nikon'],
        'cinematic': ['cinematic', 'movie', 'film', 'drama', 'lighting', 'depth of field'],
        'anime': ['anime', 'manga', 'japanese', 'studio ghibli', 'cel shade'],
        'cyberpunk': ['cyberpunk', 'neon', 'futuristic', 'sci-fi', 'digital'],
        'minimal': ['minimal', 'minimalist', 'clean', 'simple', 'modern'],
        'fantasy': ['fantasy', 'magical', 'dragon', 'medieval', 'mythical']
    }

    detected_styles = []
    for style, kw_list in style_keywords.items():
        if any(kw in prompt.lower() for kw in kw_list):
            detected_styles.append(style)
    if not detected_styles:
        detected_styles.append('general')

    keywords = [w for w in words if len(w) > 4][:8]
    if not keywords:
        keywords = words[:8]

    complexity = 'simple' if word_count < 10 else 'moderate' if word_count < 25 else 'complex'
    tone = sentiment.capitalize() if sentiment else 'Neutral'

    enhancement_suggestions = []
    if word_count < 8:
        enhancement_suggestions.append('Add more descriptive adjectives (e.g., lighting, texture, mood)')
    if 'style' not in prompt.lower():
        enhancement_suggestions.append('Specify an art style (realistic, anime, cinematic, etc.)')
    if 'color' not in prompt.lower():
        enhancement_suggestions.append('Include color palette guidance')
    if word_count < 15:
        enhancement_suggestions.append('Add technical quality terms (8k, detailed, professional)')

    return {
        'success': True,
        'word_count': word_count,
        'char_count': char_count,
        'sentiment': sentiment,
        'sentiment_scores': scores,
        'tone': tone,
        'complexity': complexity,
        'detected_styles': detected_styles,
        'keywords': keywords,
        'enhancement_suggestions': enhancement_suggestions,
        'model': 'watson-nlp-mock'
    }


def _analyze_prompt_live(prompt):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WATSON_API_KEY}'
        }
        payload = {
            'text': prompt,
            'features': {
                'sentiment': {},
                'keywords': {'limit': 10},
                'emotion': {},
                'categories': {}
            }
        }
        url = f'{WATSON_URL}/v1/analyze?version=2022-04-07'
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'success': True,
                'sentiment': data.get('sentiment', {}).get('document', {}).get('label', 'neutral'),
                'keywords': [k['text'] for k in data.get('keywords', [])],
                'emotion': data.get('emotion', {}).get('document', {}).get('emotion', {}),
                'categories': [c['label'] for c in data.get('categories', [])],
                'model': 'watson-nlu-live'
            }
        return {'success': False, 'error': f'Watson API error: {resp.status_code}'}
    except Exception as e:
        logger.error(f'Watson NLP live call failed: {e}')
        return {'success': False, 'error': str(e)}


# ─── Watson Assistant: Chatbot ────────────────────────────────────

ASSISTANT_INTENTS = {
    'greeting': {
        'keywords': ['hi', 'hello', 'hey', 'sup', 'help'],
        'response': 'Welcome to AURA AI! I\'m your AI creative assistant. Try asking me about generating images, editing, credits, or project types!'
    },
    'generate': {
        'keywords': ['generate', 'create', 'make', 'produce', 'image'],
        'response': 'To generate an image, go to the **Workspace** and type a detailed prompt. You can specify style, colors, and mood. Each generation costs 15 credits. Try something like: "a serene mountain landscape at sunset, cinematic lighting, photorealistic"'
    },
    'credits': {
        'keywords': ['credit', 'coins', 'limit', 'cost', 'price', 'free'],
        'response': 'You get **100 free credits** daily (refills every 24h). Each image generation costs **15 credits**. You can check your balance on the Dashboard.'
    },
    'editor': {
        'keywords': ['edit', 'editor', 'filter', 'adjust', 'crop', 'resize'],
        'response': 'The **Image Editor** lets you adjust brightness, contrast, saturation, blur, apply filters (vintage, HDR, neon), resize, upscale with AI, and remove backgrounds. Open any image from your gallery and click the Edit button.'
    },
    'project': {
        'keywords': ['project', 'brand', 'generator', 'assets'],
        'response': 'The **Project Generator** creates 5 brand assets from one prompt! Try types like: cafe, restaurant, startup, fashion, or app. Each project costs 75 credits (5 × 15 credits).'
    },
    'agents': {
        'keywords': ['agent', 'multi', 'studio', 'collaborate'],
        'response': 'The **Multi-Agent Studio** deploys 5 AI specialists (Creative Director, Brand Strategist, Visual Designer, UX Expert, Marketing Expert) that each generate unique images from different perspectives on your brief.'
    },
    'gallery': {
        'keywords': ['gallery', 'save', 'download', 'favorite', 'collection'],
        'response': 'Your **Gallery** stores all generated images. You can favorite them, add to collections, download, or open in the editor. Use the search bar to find images by prompt text.'
    },
    'collection': {
        'keywords': ['collection', 'folder', 'organize', 'group'],
        'response': '**Collections** help you organize images into custom folders. Create collections like "Brand Project", "Social Media", or "Inspiration" and add images from the gallery.'
    },
    'watson': {
        'keywords': ['watson', 'ibm', 'ai', 'smart', 'enhance'],
        'response': 'AURA AI uses **IBM Watson** for smart features! Watson NLP analyzes your prompts for sentiment, style detection, and enhancement suggestions. Watson Visual Recognition can classify and tag your generated images automatically.'
    },
    'demo': {
        'keywords': ['demo', 'tutorial', 'guide', 'walkthrough', 'how'],
        'response': 'Check out the **Demo** page (shown after login) for a visual walkthrough of all features! Or ask me anything specific.'
    }
}


def chat_with_assistant(message, session_id=None):
    """Process a chat message using Watson Assistant."""
    if _is_live():
        return _chat_live(message, session_id)
    return _chat_mock(message, session_id)


def _chat_mock(message, session_id=None):
    msg_lower = message.lower().strip()

    matched_intents = []
    for intent, config in ASSISTANT_INTENTS.items():
        if any(kw in msg_lower for kw in config['keywords']):
            matched_intents.append((intent, config))

    if matched_intents:
        intent_name, config = matched_intents[0]
        confidence = random.uniform(0.75, 0.98)
        return {
            'success': True,
            'response': config['response'],
            'intent': intent_name,
            'confidence': round(confidence, 2),
            'session_id': session_id or f'sess_{datetime.now().timestamp()}',
            'model': 'watson-assistant-mock'
        }

    fallback = [
        'I\'m not sure about that! Try asking about **generation**, **editing**, **credits**, **projects**, or **IBM Watson** features.',
        'Hmm, I don\'t have an answer for that yet. I can help with image generation, editing, credits, and platform features!',
        'Great question! I specialize in AURA AI topics. Try: "How do I generate an image?" or "What are AI agents?"'
    ]
    return {
        'success': True,
        'response': random.choice(fallback),
        'intent': 'unknown',
        'confidence': random.uniform(0.1, 0.4),
        'session_id': session_id or f'sess_{datetime.now().timestamp()}',
        'model': 'watson-assistant-mock'
    }


def _chat_live(message, session_id=None):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WATSON_API_KEY}'
        }
        payload = {
            'input': {'text': message},
            'assistant_id': WATSON_ASSISTANT_ID
        }
        if session_id:
            payload['session_id'] = session_id

        url = f'{WATSON_URL}/v2/assistants/{WATSON_ASSISTANT_ID}/sessions'
        if session_id:
            resp = requests.post(f'{url}/{session_id}/message', headers=headers, json=payload, timeout=15)
        else:
            sess_resp = requests.post(url, headers=headers, timeout=10)
            if sess_resp.status_code != 201:
                return {'success': False, 'error': 'Failed to create session'}
            session_id = sess_resp.json().get('session_id')
            payload.pop('assistant_id', None)
            resp = requests.post(f'{url}/{session_id}/message', headers=headers, json=payload, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            text = ''
            for msg in data.get('output', {}).get('generic', []):
                if msg.get('response_type') == 'text':
                    text += msg.get('text', '')
            return {
                'success': True,
                'response': text or 'No response from Watson.',
                'intent': data.get('output', {}).get('intents', [{}])[0].get('intent', 'unknown'),
                'confidence': data.get('output', {}).get('intents', [{}])[0].get('confidence', 0),
                'session_id': session_id,
                'model': 'watson-assistant-live'
            }
        return {'success': False, 'error': f'Watson API error: {resp.status_code}'}
    except Exception as e:
        logger.error(f'Watson Assistant live call failed: {e}')
        return {'success': False, 'error': str(e)}


# ─── Watson Visual Recognition: Image Classification ──────────────

def classify_image(image_url):
    """Classify an image using Watson Visual Recognition."""
    if _is_live():
        return _classify_image_live(image_url)
    return _classify_image_mock(image_url)


def _classify_image_mock(image_url):
    url_lower = image_url.lower()

    all_tags = {
        'style': ['Digital Art', 'Photograph', 'Illustration', '3D Render', 'Concept Art'],
        'subject': ['Landscape', 'Portrait', 'Abstract', 'Nature', 'Urban', 'Fantasy', 'Sci-Fi', 'Still Life', 'Architecture', 'Fashion'],
        'mood': ['Dramatic', 'Serene', 'Energetic', 'Moody', 'Vibrant', 'Minimal', 'Warm', 'Cool', 'Dreamy', 'Bold'],
        'color': ['Warm Tones', 'Cool Tones', 'Monochrome', 'High Contrast', 'Pastel', 'Neon', 'Earth Tones', 'Vibrant'],
        'quality': ['High Resolution', 'Professional Grade', 'Detailed Texture', 'Smooth Gradients', 'Sharp Focus']
    }

    tags = {}
    for category, options in all_tags.items():
        tags[category] = [random.choice(options)]

    return {
        'success': True,
        'tags': tags,
        'description': f"A {tags['style'][0].lower()} featuring {tags['subject'][0].lower()} with {tags['mood'][0].lower()} mood and {tags['color'][0].lower()} palette.",
        'model': 'watson-vr-mock'
    }


def _classify_image_live(image_url):
    try:
        headers = {'Authorization': f'Bearer {WATSON_API_KEY}'}
        params = {'url': image_url, 'version': '2022-06-01', 'threshold': 0.6}
        url = f'{WATSON_URL}/v3/classify'
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            classes = data.get('images', [{}])[0].get('classifiers', [{}])[0].get('classes', [])
            return {
                'success': True,
                'tags': {
                    'watson_classes': [c['class'] for c in classes[:10]],
                    'scores': {c['class']: c['score'] for c in classes[:5]}
                },
                'description': ', '.join([c['class'] for c in classes[:5]]),
                'model': 'watson-vr-live'
            }
        return {'success': False, 'error': f'Watson API error: {resp.status_code}'}
    except Exception as e:
        logger.error(f'Watson VR live call failed: {e}')
        return {'success': False, 'error': str(e)}


def enhance_prompt(prompt):
    """Enhance a creative prompt using Watson NLP insights."""
    analysis = analyze_prompt(prompt)
    if not analysis.get('success'):
        return {'success': False, 'error': 'Analysis failed'}

    suggestions = analysis.get('enhancement_suggestions', [])
    detected_styles = analysis.get('detected_styles', [])
    keywords = analysis.get('keywords', [])

    enhancements = []
    if 'realistic' not in detected_styles and 'general' in detected_styles:
        enhancements.append('photorealistic, 8k, highly detailed')
    if len(keywords) < 5:
        enhancements.append('professional lighting, sharp focus, masterpiece quality')
    if 'cinematic' not in detected_styles:
        enhancements.append('cinematic composition')

    enhanced = prompt
    if enhancements:
        enhanced = prompt + ', ' + ', '.join(enhancements[:3])

    return {
        'success': True,
        'original': prompt,
        'enhanced': enhanced,
        'suggestions': suggestions,
        'enhancements_applied': enhancements[:3],
        'style_suggestions': detected_styles,
        'model': 'watson-enhancer-mock'
    }
