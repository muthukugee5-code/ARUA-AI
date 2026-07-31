"""
AURA AI - Profile API
User profile management and settings
"""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from utils.supabase_client import supabase_query, upload_to_storage

logger = logging.getLogger(__name__)
profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile."""
    user_id = g.user_id
    try:
        profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
        profile = profiles[0] if profiles else {}
        
        return jsonify({
            'success': True,
            'profile': {
                'user_id': user_id,
                'email': g.user.get('email'),
                'username': profile.get('username'),
                'bio': profile.get('bio', ''),
                'avatar_url': profile.get('avatar_url'),
                'ai_credits': profile.get('ai_credits', 0),
                'total_generated': profile.get('total_generated', 0),
                'storage_used': profile.get('storage_used', 0),
                'role': profile.get('role', 'user'),
                'created_at': profile.get('created_at'),
                'last_login': profile.get('last_login')
            }
        }), 200
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Failed to fetch profile'}), 500


@profile_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile information."""
    user_id = g.user_id
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    allowed_fields = ['username', 'bio']
    update_data = {}
    
    for field in allowed_fields:
        if field in data:
            value = str(data[field]).strip()
            if field == 'username':
                if len(value) < 3:
                    return jsonify({'error': 'Username must be at least 3 characters'}), 400
                import re
                if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
                    return jsonify({'error': 'Invalid username characters'}), 400
            update_data[field] = value
    
    if not update_data:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    try:
        supabase_query(
            f"profiles?user_id=eq.{user_id}",
            method='PATCH',
            data=update_data,
            use_service_key=True
        )
        
        return jsonify({'success': True, 'message': 'Profile updated', 'updated': update_data}), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500


@profile_bp.route('/profile/avatar', methods=['POST'])
@require_auth
def upload_avatar():
    """Upload user avatar image."""
    user_id = g.user_id
    
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['avatar']
    
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_types = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
    if file.content_type not in allowed_types:
        return jsonify({'error': 'Invalid file type. Use JPEG, PNG, WebP, or GIF'}), 400
    
    # Check file size (2MB limit for avatars)
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 2 * 1024 * 1024:
        return jsonify({'error': 'Avatar must be under 2MB'}), 400
    
    try:
        from PIL import Image
        import io
        
        # Resize avatar to 256x256
        img = Image.open(file).convert('RGB')
        img = img.resize((256, 256), Image.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        
        file_path = f"avatars/{user_id}/avatar.jpg"
        public_url = upload_to_storage('arua-avatars', file_path, buffer.read(), 'image/jpeg')
        
        if not public_url:
            return jsonify({'error': 'Upload failed'}), 500
        
        # Update profile
        supabase_query(
            f"profiles?user_id=eq.{user_id}",
            method='PATCH',
            data={'avatar_url': public_url},
            use_service_key=True
        )
        
        return jsonify({
            'success': True,
            'avatar_url': public_url
        }), 200
        
    except Exception as e:
        logger.error(f"Avatar upload error: {e}")
        return jsonify({'error': 'Avatar upload failed'}), 500


@profile_bp.route('/history', methods=['GET'])
@require_auth
def get_history():
    """Get user's prompt history."""
    user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 50)
    offset = (page - 1) * per_page
    
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/prompt_history?user_id=eq.{user_id}&order=created_at.desc&limit={per_page}&offset={offset}"
        headers = get_headers(use_service_key=True)
        headers['Prefer'] = 'count=exact'
        
        response = req.get(url, headers=headers, timeout=10)
        history = response.json() if response.text else []
        
        return jsonify({
            'success': True,
            'history': history if isinstance(history, list) else [],
            'page': page
        }), 200
        
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return jsonify({'error': 'Failed to fetch history'}), 500
