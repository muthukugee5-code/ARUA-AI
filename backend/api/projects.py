"""
ARUA AI - Creative Project Generator
One prompt generates an entire project: logo, website UI, posters, color palette, and more
"""

import os
import uuid
import logging
import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from utils.supabase_client import supabase_query
from api.generate import build_generation_url, get_dimensions, POLLINATIONS_BASE

logger = logging.getLogger(__name__)
projects_bp = Blueprint('projects', __name__)

PROJECT_ASSETS = {
    'cafe': {
        'name': 'Gaming Café',
        'assets': [
            {'type': 'logo', 'prompt_suffix': 'logo for a gaming cafe, neon sign style, red and black, vector', 'style': 'minimal', 'ratio': '1:1'},
            {'type': 'poster', 'prompt_suffix': 'promotional poster for a gaming cafe, esports tournament, neon lights, cyberpunk', 'style': 'cyberpunk', 'ratio': '4:3'},
            {'type': 'ui_mobile', 'prompt_suffix': 'mobile app UI for a gaming cafe loyalty program, dark theme, neon accents', 'style': 'minimal', 'ratio': '9:16'},
            {'type': 'color_palette', 'prompt_suffix': 'color palette swatches for gaming cafe brand, red black neon green, modern', 'style': 'minimal', 'ratio': '16:9'},
            {'type': 'social', 'prompt_suffix': 'Instagram post design for gaming cafe, new menu items, vibrant, engaging', 'style': 'cinematic', 'ratio': '1:1'},
        ]
    },
    'restaurant': {
        'name': 'Restaurant',
        'assets': [
            {'type': 'logo', 'prompt_suffix': 'elegant restaurant logo, fine dining, gold and maroon, sophisticated', 'style': 'luxury', 'ratio': '1:1'},
            {'type': 'poster', 'prompt_suffix': 'restaurant menu board design, gourmet dishes, warm lighting, appetizing', 'style': 'realistic', 'ratio': '4:3'},
            {'type': 'ui_mobile', 'prompt_suffix': 'food delivery app UI, restaurant online ordering, clean modern design', 'style': 'minimal', 'ratio': '9:16'},
            {'type': 'business_card', 'prompt_suffix': 'elegant business card for restaurant, gold foil, minimalist, premium', 'style': 'luxury', 'ratio': '16:9'},
            {'type': 'social', 'prompt_suffix': 'social media post for restaurant, chef special, food photography style', 'style': 'realistic', 'ratio': '1:1'},
        ]
    },
    'startup': {
        'name': 'Tech Startup',
        'assets': [
            {'type': 'logo', 'prompt_suffix': 'modern tech startup logo, geometric, blue and white, innovative', 'style': 'minimal', 'ratio': '1:1'},
            {'type': 'ui_web', 'prompt_suffix': 'SaaS dashboard UI design, dark mode, clean analytics, modern', 'style': 'minimal', 'ratio': '16:9'},
            {'type': 'poster', 'prompt_suffix': 'product launch banner for tech startup, sleek, professional, exciting', 'style': 'cinematic', 'ratio': '4:3'},
            {'type': 'color_palette', 'prompt_suffix': 'brand color palette for tech startup, blue gradient, modern swatches', 'style': 'minimal', 'ratio': '16:9'},
            {'type': 'social', 'prompt_suffix': 'LinkedIn banner for tech startup, team photo style, professional', 'style': 'cinematic', 'ratio': '16:9'},
        ]
    },
    'fashion': {
        'name': 'Fashion Brand',
        'assets': [
            {'type': 'logo', 'prompt_suffix': 'fashion brand logo, elegant typography, minimalist, high end', 'style': 'luxury', 'ratio': '1:1'},
            {'type': 'poster', 'prompt_suffix': 'fashion collection poster, model wearing designer outfit, editorial', 'style': 'hyper_realistic', 'ratio': '4:3'},
            {'type': 'ui_mobile', 'prompt_suffix': 'fashion ecommerce app UI, clean product showcase, modern', 'style': 'minimal', 'ratio': '9:16'},
            {'type': 'business_card', 'prompt_suffix': 'fashion brand business card, minimalist, elegant, premium feel', 'style': 'luxury', 'ratio': '16:9'},
            {'type': 'social', 'prompt_suffix': 'Instagram fashion post, outfit of the day, lifestyle photography', 'style': 'hyper_realistic', 'ratio': '1:1'},
        ]
    },
    'app': {
        'name': 'Mobile App',
        'assets': [
            {'type': 'logo', 'prompt_suffix': 'mobile app icon, minimalist, gradient, modern, recognizable', 'style': 'minimal', 'ratio': '1:1'},
            {'type': 'ui_mobile', 'prompt_suffix': 'mobile app onboarding screens, clean UI, modern illustrations', 'style': 'minimal', 'ratio': '9:16'},
            {'type': 'poster', 'prompt_suffix': 'app store promotional banner, app features showcase, vibrant', 'style': 'cinematic', 'ratio': '16:9'},
            {'type': 'ui_web', 'prompt_suffix': 'app landing page design, hero section, call to action, clean', 'style': 'minimal', 'ratio': '16:9'},
            {'type': 'social', 'prompt_suffix': 'social media teaser for new app launch, eye catching, modern', 'style': 'cinematic', 'ratio': '1:1'},
        ]
    }
}

AGENTS = [
    {'role': 'Creative Director', 'icon': '🎯', 'color': '#dc2626',
     'prompt': 'As a Creative Director, define the creative vision and brand strategy for: {prompt}. Output a brief creative direction (2-3 sentences).',
     'image_prompt': 'Abstract artistic composition representing {prompt}, fluid organic shapes in red and black, gold accents, dramatic lighting, gallery quality art print, elegant and sophisticated, ultra detailed 8k',
     'style': 'cinematic', 'ratio': '4:3'},
    {'role': 'Brand Strategist', 'icon': '📊', 'color': '#5b8def',
     'prompt': 'As a Brand Strategist, define the brand identity, target audience, and market positioning for: {prompt}. Output a concise brand strategy.',
     'image_prompt': 'Abstract geometric patterns and data visualization style design for {prompt}, interconnected nodes and flowing lines, deep blue and silver, futuristic clean aesthetic, professional 8k',
     'style': 'minimal', 'ratio': '16:9'},
    {'role': 'Visual Designer', 'icon': '🎨', 'color': '#e055a9',
     'prompt': 'As a Visual Designer, suggest color palette, typography, and visual style recommendations for: {prompt}. Output specific design choices.',
     'image_prompt': 'Beautiful color gradient abstract art for {prompt}, smooth transitions between deep red and gold, flowing silk texture, luxury brand aesthetic, museum quality 8k',
     'style': 'luxury', 'ratio': '1:1'},
    {'role': 'UX Expert', 'icon': '🧠', 'color': '#00d084',
     'prompt': 'As a UX Expert, analyze the user experience and accessibility considerations for: {prompt}. Output UX recommendations.',
     'image_prompt': 'Clean minimal app interface concept for {prompt}, modern glassmorphism design, rounded elements, soft shadows, elegant dark mode UI, app showcase quality 8k',
     'style': 'minimal', 'ratio': '9:16'},
    {'role': 'Marketing Expert', 'icon': '📈', 'color': '#f5a623',
     'prompt': 'As a Marketing Expert, create a marketing strategy and content plan for: {prompt}. Output key marketing tactics.',
     'image_prompt': 'Vibrant abstract brand campaign concept for {prompt}, dynamic composition with glowing particles and light beams, energetic and modern, social media aesthetic, high quality 8k',
     'style': 'cinematic', 'ratio': '16:9'},
]


@projects_bp.route('/generate/project', methods=['POST'])
@require_auth
def generate_project():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    project_type = data.get('type', '').strip()

    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400

    template = PROJECT_ASSETS.get(project_type)
    if not template:
        return jsonify({'error': 'Invalid project type', 'types': list(PROJECT_ASSETS.keys())}), 400

    project_id = str(uuid.uuid4())
    assets = []
    quality = 'standard'
    resolution = 'hd'

    for asset_def in template['assets']:
        try:
            full_prompt = f"{template['name']}: {prompt}, {asset_def['prompt_suffix']}"
            width, height = get_dimensions(asset_def['ratio'], resolution)
            url = build_generation_url(full_prompt, width, height)
            assets.append({
                'type': asset_def['type'],
                'style': asset_def['style'],
                'url': url,
                'width': width,
                'height': height,
                'prompt': full_prompt
            })
        except Exception as e:
            logger.warning(f"Asset failed: {e}")

    try:
        supabase_query('projects', method='POST', data={
            'id': project_id,
            'user_id': g.user_id,
            'title': f"{template['name']}: {prompt[:50]}",
            'project_type': project_type,
            'prompt': prompt,
            'assets': json.dumps(assets),
            'created_at': datetime.utcnow().isoformat()
        }, use_service_key=True)
    except Exception as e:
        logger.warning(f"Project save failed: {e}")

    return jsonify({
        'success': True,
        'project_id': project_id,
        'title': f"{template['name']}: {prompt[:50]}",
        'project_type': project_type,
        'assets': assets
    }), 200


@projects_bp.route('/projects', methods=['GET'])
@require_auth
def get_projects():
    try:
        records = supabase_query('projects', filters={'user_id': g.user_id}, use_service_key=True)
        for r in records:
            if isinstance(r.get('assets'), str):
                r['assets'] = json.loads(r['assets'])
        return jsonify({'success': True, 'projects': records or []}), 200
    except Exception as e:
        logger.error(f"Fetch projects error: {e}")
        return jsonify({'error': 'Failed to load projects'}), 500


@projects_bp.route('/generate/project-types', methods=['GET'])
def get_project_types():
    types = {k: {'name': v['name'], 'asset_count': len(v['assets'])} for k, v in PROJECT_ASSETS.items()}
    return jsonify({'success': True, 'types': types}), 200


@projects_bp.route('/agents/generate', methods=['POST'])
@require_auth
def generate_agents():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()

    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400

    results = []
    for agent in AGENTS:
        try:
            agent_prompt = agent['prompt'].format(prompt=prompt)
            image_prompt = agent.get('image_prompt', prompt).format(prompt=prompt)
            style = agent.get('style', 'sd')
            ratio = agent.get('ratio', '1:1')
            width, height = get_dimensions(ratio, '4k')
            url = build_generation_url(image_prompt, width, height, model='flux')
            results.append({
                'role': agent['role'],
                'icon': agent['icon'],
                'color': agent['color'],
                'url': url,
                'style': style,
                'ratio': ratio,
                'prompt': agent_prompt,
                'image_prompt': image_prompt
            })
        except Exception as e:
            logger.warning(f"Agent {agent['role']} failed: {e}")

    return jsonify({
        'success': True,
        'prompt': prompt,
        'agents': results
    }), 200


@projects_bp.route('/agents/generate-smart', methods=['POST'])
@require_auth
def generate_agents_smart():
    """Generate agent responses using Gemini (text) + Pollinations (image)."""
    from utils.gemini import call_gemini, AGENT_SYSTEM_PROMPTS, is_available

    data = request.get_json()
    prompt = data.get('prompt', '').strip()

    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400

    if not is_available():
        return jsonify({'error': 'Gemini not configured', 'message': 'GEMINI_API_KEY not set. Use the standard agent mode instead.'}), 400

    results = []
    for agent in AGENTS:
        role = agent['role']
        role_config = AGENT_SYSTEM_PROMPTS.get(role, {})
        try:
            gemini_text = call_gemini(prompt, role_config.get('system', ''))
            image_prompt = agent.get('image_prompt', prompt).format(prompt=prompt)
            style = agent.get('style', 'sd')
            ratio = agent.get('ratio', '1:1')
            width, height = get_dimensions(ratio, '4k')
            url = build_generation_url(image_prompt, width, height, model='flux')
            results.append({
                'role': role,
                'icon': role_config.get('icon', agent['icon']),
                'color': role_config.get('color', agent['color']),
                'url': url,
                'style': style,
                'ratio': ratio,
                'text': gemini_text or f"As {role}, I'd focus on: {prompt}",
                'prompt': agent['prompt'].format(prompt=prompt),
                'image_prompt': image_prompt
            })
        except Exception as e:
            logger.warning(f"Smart agent {role} failed: {e}")

    return jsonify({
        'success': True,
        'prompt': prompt,
        'agents': results,
        'powered_by': 'gemini'
    }), 200


@projects_bp.route('/agents/roles', methods=['GET'])
def get_agent_roles():
    roles = [{'role': a['role'], 'icon': a['icon'], 'color': a['color']} for a in AGENTS]
    return jsonify({'success': True, 'agents': roles}), 200


@projects_bp.route('/agents/save', methods=['POST'])
@require_auth
def save_agent_session():
    """Save an agent generation session to local file."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    agents = data.get('agents', [])

    if not prompt or not agents:
        return jsonify({'error': 'Prompt and agents required'}), 400

    session_id = str(uuid.uuid4())
    session = {
        'id': session_id,
        'user_id': g.user_id,
        'prompt': prompt,
        'agents': agents,
        'created_at': datetime.utcnow().isoformat()
    }

    try:
        sessions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'agent_sessions')
        os.makedirs(sessions_dir, exist_ok=True)
        filepath = os.path.join(sessions_dir, f"{session_id}.json")
        with open(filepath, 'w') as f:
            json.dump(session, f)
        return jsonify({'success': True, 'session_id': session_id}), 200
    except Exception as e:
        logger.error(f"Save session error: {e}")
        return jsonify({'error': 'Failed to save session'}), 500


@projects_bp.route('/agents/history', methods=['GET'])
@require_auth
def get_agent_history():
    """Get all agent sessions from local files."""
    try:
        sessions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'agent_sessions')
        sessions = []
        if os.path.exists(sessions_dir):
            for fname in sorted(os.listdir(sessions_dir), reverse=True)[:50]:
                if fname.endswith('.json'):
                    with open(os.path.join(sessions_dir, fname)) as f:
                        sessions.append(json.load(f))
        return jsonify({'success': True, 'sessions': sessions}), 200
    except Exception as e:
        logger.error(f"Fetch sessions error: {e}")
        return jsonify({'error': 'Failed to load sessions'}), 500
