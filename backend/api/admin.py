"""
AURA AI - Admin API
Platform management, user administration, and analytics
"""

import logging
from flask import Blueprint, request, jsonify
from utils.auth_middleware import require_admin
from utils.supabase_client import supabase_query

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/stats', methods=['GET'])
@require_admin
def get_platform_stats():
    """Get platform-wide statistics."""
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        headers = get_headers(use_service_key=True)
        count_headers = {**headers, 'Prefer': 'count=exact'}
        
        # Total users
        users_resp = req.get(f"{SUPABASE_URL}/rest/v1/profiles", headers=count_headers, timeout=10)
        users_range = users_resp.headers.get('Content-Range', '0/0').split('/')
        total_users = int(users_range[-1]) if users_range[-1] != '*' else 0
        
        # Total images
        images_resp = req.get(f"{SUPABASE_URL}/rest/v1/generated_images", headers=count_headers, timeout=10)
        images_range = images_resp.headers.get('Content-Range', '0/0').split('/')
        total_images = int(images_range[-1]) if images_range[-1] != '*' else 0
        
        # Active today
        from datetime import datetime
        today = datetime.utcnow().strftime('%Y-%m-%d')
        active_url = f"{SUPABASE_URL}/rest/v1/activity_logs?created_at=gte.{today}T00:00:00"
        active_resp = req.get(active_url, headers=count_headers, timeout=10)
        active_range = active_resp.headers.get('Content-Range', '0/0').split('/')
        active_today = int(active_range[-1]) if active_range[-1] != '*' else 0
        
        # Recent users
        recent_users_url = f"{SUPABASE_URL}/rest/v1/profiles?order=created_at.desc&limit=10"
        recent_resp = req.get(recent_users_url, headers=headers, timeout=10)
        recent_users = recent_resp.json() if recent_resp.text else []
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_images': total_images,
                'active_today': active_today
            },
            'recent_users': recent_users if isinstance(recent_users, list) else []
        }), 200
        
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return jsonify({'error': 'Failed to fetch admin stats'}), 500


@admin_bp.route('/admin/users', methods=['GET'])
@require_admin
def get_users():
    """Get all platform users."""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 50)
    offset = (page - 1) * per_page
    
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/profiles?order=created_at.desc&limit={per_page}&offset={offset}"
        headers = get_headers(use_service_key=True)
        headers['Prefer'] = 'count=exact'
        
        response = req.get(url, headers=headers, timeout=10)
        users = response.json() if response.text else []
        total_range = response.headers.get('Content-Range', '0/0').split('/')
        total = int(total_range[-1]) if total_range[-1] != '*' else 0
        
        return jsonify({
            'success': True,
            'users': users if isinstance(users, list) else [],
            'total': total,
            'page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Admin get users error: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500


@admin_bp.route('/admin/users/<user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete a user account and all their data."""
    try:
        # Delete user images
        supabase_query(
            f"generated_images?user_id=eq.{user_id}",
            method='DELETE', use_service_key=True
        )
        # Delete user profile
        supabase_query(
            f"profiles?user_id=eq.{user_id}",
            method='DELETE', use_service_key=True
        )
        
        return jsonify({'success': True, 'message': 'User deleted'}), 200
    except Exception as e:
        logger.error(f"Admin delete user error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500


@admin_bp.route('/admin/images', methods=['GET'])
@require_admin
def get_all_images():
    """Get all platform images."""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 50)
    offset = (page - 1) * per_page
    
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/generated_images?order=created_at.desc&limit={per_page}&offset={offset}"
        headers = get_headers(use_service_key=True)
        headers['Prefer'] = 'count=exact'
        
        response = req.get(url, headers=headers, timeout=10)
        images = response.json() if response.text else []
        total_range = response.headers.get('Content-Range', '0/0').split('/')
        total = int(total_range[-1]) if total_range[-1] != '*' else 0
        
        return jsonify({
            'success': True,
            'images': images if isinstance(images, list) else [],
            'total': total,
            'page': page
        }), 200
    except Exception as e:
        logger.error(f"Admin get images error: {e}")
        return jsonify({'error': 'Failed to fetch images'}), 500
