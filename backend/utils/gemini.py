"""
Gemini AI - Google's LLM integration for AURA AI agents
"""

import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

AGENT_SYSTEM_PROMPTS = {
    'Creative Director': {
        'system': "You are an expert Creative Director. Define the creative vision, brand narrative, and emotional tone for the project. Output 2-3 concise paragraphs with specific creative direction. Be visionary and inspirational.",
        'color': '#dc2626', 'icon': '🎯'
    },
    'Brand Strategist': {
        'system': "You are a senior Brand Strategist. Define target audience, brand positioning, market differentiation, and personality traits. Output a concise brand strategy with audience segments and positioning statement.",
        'color': '#5b8def', 'icon': '📊'
    },
    'Visual Designer': {
        'system': "You are a Visual Designer. Recommend specific color palette (with hex codes), typography pairings, visual style, and design system guidelines. Be specific and actionable with your recommendations.",
        'color': '#e055a9', 'icon': '🎨'
    },
    'UX Expert': {
        'system': "You are a UX expert. Analyze the user journey, information architecture, accessibility needs, and interaction design. Output UX recommendations covering flow, accessibility, and key interactions.",
        'color': '#00d084', 'icon': '🧠'
    },
    'Marketing Expert': {
        'system': "You are a Marketing Expert. Create a go-to-market strategy with campaign ideas, channel recommendations, and content strategy. Output specific marketing tactics and channel mix.",
        'color': '#f5a623', 'icon': '📈'
    }
}


def call_gemini(prompt, system_prompt=None):
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set")
        return None

    headers = {'Content-Type': 'application/json'}
    full_prompt = f"{system_prompt}\n\nProject: {prompt}" if system_prompt else prompt

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 512,
            "topP": 0.95
        }
    }

    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        if resp.status_code != 200:
            logger.error(f"Gemini API error {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        candidates = data.get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            return text.strip()
        return None
    except requests.exceptions.Timeout:
        logger.error("Gemini API timeout")
        return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


def is_available():
    return bool(GEMINI_API_KEY)
