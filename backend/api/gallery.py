"""
AURA AI - Gallery API
Image retrieval, favorites, downloads, and management
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, rate_limit
from utils.supabase_client import supabase_query

logger = logging.getLogger(__name__)
gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/gallery', methods=['GET'])
@require_auth
def get_gallery():
    """Get user's image gallery with filtering and pagination."""
    user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 50)
    style = request.args.get('style')
    category = request.args.get('category')
    favorites_only = request.args.get('favorites') == 'true'
    sort = request.args.get('sort', 'newest')
    search = request.args.get('search', '').strip()
    
    try:
        url_params = [f"user_id=eq.{user_id}"]
        
        if style:
            url_params.append(f"style=eq.{style}")
        if category:
            url_params.append(f"category=eq.{category}")
        if favorites_only:
            url_params.append("is_favorite=eq.true")
        
        # Sorting
        order = 'created_at.desc' if sort == 'newest' else 'created_at.asc'
        if sort == 'popular':
            order = 'downloads.desc'
        url_params.append(f"order={order}")
        
        # Pagination
        offset = (page - 1) * per_page
        url_params.append(f"limit={per_page}&offset={offset}")
        
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/generated_images?{'&'.join(url_params)}"
        if search:
            url += f"&prompt=ilike.*{search}*"
        
        headers = get_headers(use_service_key=True)
        headers['Prefer'] = 'count=exact'
        
        response = req.get(url, headers=headers, timeout=10)
        images = response.json() if response.text else []
        
        # Get total count from headers
        total = response.headers.get('Content-Range', '').split('/')
        total_count = int(total[-1]) if len(total) > 1 and total[-1] != '*' else len(images)
        
        return jsonify({
            'success': True,
            'images': images if isinstance(images, list) else [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Gallery fetch error: {e}")
        return jsonify({'error': 'Failed to fetch gallery'}), 500


@gallery_bp.route('/gallery/<image_id>', methods=['GET'])
@require_auth
def get_image(image_id):
    """Get a single image by ID."""
    user_id = g.user_id
    
    try:
        images = supabase_query(
            'generated_images',
            filters={'id': image_id, 'user_id': user_id},
            use_service_key=True
        )
        
        if not images:
            return jsonify({'error': 'Image not found'}), 404
        
        return jsonify({'success': True, 'image': images[0]}), 200
        
    except Exception as e:
        logger.error(f"Get image error: {e}")
        return jsonify({'error': 'Failed to fetch image'}), 500


@gallery_bp.route('/favorite', methods=['POST'])
@require_auth
def toggle_favorite():
    """Toggle image favorite status."""
    data = request.get_json()
    image_id = data.get('image_id')
    
    if not image_id:
        return jsonify({'error': 'Image ID required'}), 400
    
    user_id = g.user_id
    
    try:
        images = supabase_query(
            'generated_images',
            filters={'id': image_id, 'user_id': user_id},
            use_service_key=True
        )
        
        if not images:
            return jsonify({'error': 'Image not found or unauthorized'}), 404
        
        current_status = images[0].get('is_favorite', False)
        new_status = not current_status
        
        supabase_query(
            f"generated_images?id=eq.{image_id}&user_id=eq.{user_id}",
            method='PATCH',
            data={'is_favorite': new_status},
            use_service_key=True
        )
        
        return jsonify({
            'success': True,
            'image_id': image_id,
            'is_favorite': new_status
        }), 200
        
    except Exception as e:
        logger.error(f"Favorite toggle error: {e}")
        return jsonify({'error': 'Failed to toggle favorite'}), 500


@gallery_bp.route('/image/<image_id>', methods=['DELETE'])
@require_auth
def delete_image(image_id):
    """Delete an image from the gallery."""
    user_id = g.user_id
    
    try:
        images = supabase_query(
            'generated_images',
            filters={'id': image_id, 'user_id': user_id},
            use_service_key=True
        )
        
        if not images:
            return jsonify({'error': 'Image not found or unauthorized'}), 404
        
        supabase_query(
            f"generated_images?id=eq.{image_id}&user_id=eq.{user_id}",
            method='DELETE',
            use_service_key=True
        )
        
        return jsonify({'success': True, 'message': 'Image deleted'}), 200
        
    except Exception as e:
        logger.error(f"Delete image error: {e}")
        return jsonify({'error': 'Failed to delete image'}), 500


@gallery_bp.route('/favorites', methods=['GET'])
@require_auth
def get_favorites():
    """Get all favorited images."""
    user_id = g.user_id
    
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/generated_images?user_id=eq.{user_id}&is_favorite=eq.true&order=created_at.desc"
        headers = get_headers(use_service_key=True)
        
        response = req.get(url, headers=headers, timeout=10)
        images = response.json() if response.text else []
        
        return jsonify({
            'success': True,
            'favorites': images if isinstance(images, list) else []
        }), 200
        
    except Exception as e:
        logger.error(f"Favorites fetch error: {e}")
        return jsonify({'error': 'Failed to fetch favorites'}), 500


@gallery_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Get dashboard statistics and recent activity."""
    user_id = g.user_id
    
    try:
        # Get profile
        profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
        profile = profiles[0] if profiles else {}
        
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        headers = get_headers(use_service_key=True)
        
        # Recent images (last 8)
        recent_url = f"{SUPABASE_URL}/rest/v1/generated_images?user_id=eq.{user_id}&order=created_at.desc&limit=8"
        recent_resp = req.get(recent_url, headers=headers, timeout=10)
        recent_images = recent_resp.json() if recent_resp.text else []
        
        # Today's generations
        today = datetime.utcnow().strftime('%Y-%m-%d')
        today_url = f"{SUPABASE_URL}/rest/v1/generated_images?user_id=eq.{user_id}&created_at=gte.{today}T00:00:00"
        today_headers = {**headers, 'Prefer': 'count=exact'}
        today_resp = req.get(today_url, headers=today_headers, timeout=10)
        today_range = today_resp.headers.get('Content-Range', '0/0').split('/')
        today_count = int(today_range[-1]) if today_range[-1] != '*' else 0
        
        # Favorites count
        fav_url = f"{SUPABASE_URL}/rest/v1/generated_images?user_id=eq.{user_id}&is_favorite=eq.true"
        fav_headers = {**headers, 'Prefer': 'count=exact'}
        fav_resp = req.get(fav_url, headers=fav_headers, timeout=10)
        fav_range = fav_resp.headers.get('Content-Range', '0/0').split('/')
        fav_count = int(fav_range[-1]) if fav_range[-1] != '*' else 0
        
        # Collections count
        coll_url = f"{SUPABASE_URL}/rest/v1/collections?user_id=eq.{user_id}"
        coll_headers = {**headers, 'Prefer': 'count=exact'}
        coll_resp = req.get(coll_url, headers=coll_headers, timeout=10)
        coll_range = coll_resp.headers.get('Content-Range', '0/0').split('/')
        coll_count = int(coll_range[-1]) if coll_range[-1] != '*' else 0
        
        # Recent activity
        activity_url = f"{SUPABASE_URL}/rest/v1/activity_logs?user_id=eq.{user_id}&order=created_at.desc&limit=10"
        activity_resp = req.get(activity_url, headers=headers, timeout=10)
        activity = activity_resp.json() if activity_resp.text else []
        
        # Weekly stats (simplified)
        weekly_stats = []
        from datetime import timedelta
        for i in range(6, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            day_url = f"{SUPABASE_URL}/rest/v1/generated_images?user_id=eq.{user_id}&created_at=gte.{day_str}T00:00:00&created_at=lt.{day_str}T23:59:59"
            day_headers = {**headers, 'Prefer': 'count=exact'}
            day_resp = req.get(day_url, headers=day_headers, timeout=5)
            day_range = day_resp.headers.get('Content-Range', '0/0').split('/')
            day_count_val = int(day_range[-1]) if day_range[-1] != '*' else 0
            weekly_stats.append({
                'date': day.strftime('%a'),
                'count': day_count_val
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_generated': profile.get('total_generated', 0),
                'today_generated': today_count,
                'favorites': fav_count,
                'collections': coll_count,
                'ai_credits': profile.get('ai_credits', 0),
                'storage_used': profile.get('storage_used', 0)
            },
            'recent_images': recent_images if isinstance(recent_images, list) else [],
            'activity': activity if isinstance(activity, list) else [],
            'weekly_stats': weekly_stats,
            'profile': {
                'username': profile.get('username'),
                'avatar_url': profile.get('avatar_url'),
                'ai_credits': profile.get('ai_credits', 0)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': 'Failed to load dashboard'}), 500
