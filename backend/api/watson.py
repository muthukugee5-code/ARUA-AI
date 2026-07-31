"""
AURA AI - IBM Watson API Endpoints
NLP analysis, Assistant chatbot, Visual Recognition
"""

import logging
from flask import Blueprint, request, jsonify
from utils.auth_middleware import require_auth, rate_limit
from utils.watson import analyze_prompt, chat_with_assistant, classify_image, enhance_prompt

logger = logging.getLogger(__name__)
watson_bp = Blueprint('watson', __name__)


@watson_bp.route('/watson/analyze', methods=['POST'])
@require_auth
@rate_limit(max_requests=30, window=60)
def analyze():
    """Analyze a creative prompt using Watson NLP."""
    data = request.get_json()
    if not data or not data.get('prompt'):
        return jsonify({'error': 'Prompt required'}), 400

    prompt = data['prompt'].strip()
    if len(prompt) < 3:
        return jsonify({'error': 'Prompt too short'}), 400

    result = analyze_prompt(prompt)
    if result.get('success'):
        return jsonify(result), 200
    return jsonify({'error': 'Analysis failed', 'message': result.get('error', 'Unknown error')}), 500


@watson_bp.route('/watson/enhance', methods=['POST'])
@require_auth
@rate_limit(max_requests=20, window=60)
def enhance():
    """Enhance a prompt using Watson NLP insights."""
    data = request.get_json()
    if not data or not data.get('prompt'):
        return jsonify({'error': 'Prompt required'}), 400

    result = enhance_prompt(data['prompt'].strip())
    if result.get('success'):
        return jsonify(result), 200
    return jsonify({'error': 'Enhancement failed', 'message': result.get('error', 'Unknown error')}), 500


@watson_bp.route('/watson/chat', methods=['POST'])
@require_auth
@rate_limit(max_requests=30, window=60)
def chat():
    """Chat with Watson Assistant."""
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'Message required'}), 400

    result = chat_with_assistant(
        data['message'].strip(),
        session_id=data.get('session_id')
    )
    if result.get('success'):
        return jsonify(result), 200
    return jsonify({'error': 'Chat failed', 'message': result.get('error', 'Unknown error')}), 500


@watson_bp.route('/watson/classify', methods=['POST'])
@require_auth
@rate_limit(max_requests=20, window=60)
def classify():
    """Classify an image using Watson Visual Recognition."""
    data = request.get_json()
    if not data or not data.get('image_url'):
        return jsonify({'error': 'Image URL required'}), 400

    result = classify_image(data['image_url'])
    if result.get('success'):
        return jsonify(result), 200
    return jsonify({'error': 'Classification failed', 'message': result.get('error', 'Unknown error')}), 500


@watson_bp.route('/watson/status', methods=['GET'])
@require_auth
def status():
    """Get Watson integration status."""
    from utils.watson import WATSON_MODE, WATSON_API_KEY, WATSON_URL
    return jsonify({
        'mode': WATSON_MODE,
        'configured': bool(WATSON_API_KEY and WATSON_URL),
        'services': {
            'nlp': True,
            'assistant': True,
            'visual_recognition': True
        },
        'message': 'IBM Watson integration is active. ' + (
            'Running in LIVE mode.' if WATSON_MODE == 'live' and WATSON_API_KEY
            else 'Running in DEMO mode (mock data). Set WATSON_MODE=live and add API keys for production.'
        )
    }), 200
