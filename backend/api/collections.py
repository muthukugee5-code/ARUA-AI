"""
ARUA AI - Collections API
Organize images into named folders/collections
"""

import uuid
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from utils.supabase_client import supabase_query

logger = logging.getLogger(__name__)
collections_bp = Blueprint('collections', __name__)


@collections_bp.route('/collections', methods=['GET'])
@require_auth
def get_collections():
    """Get all user collections."""
    user_id = g.user_id
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/collections?user_id=eq.{user_id}&order=created_at.desc"
        response = req.get(url, headers=get_headers(use_service_key=True), timeout=10)
        collections = response.json() if response.text else []
        
        return jsonify({'success': True, 'collections': collections if isinstance(collections, list) else []}), 200
    except Exception as e:
        logger.error(f"Collections fetch error: {e}")
        return jsonify({'error': 'Failed to fetch collections'}), 500


@collections_bp.route('/collections', methods=['POST'])
@require_auth
def create_collection():
    """Create a new collection."""
    user_id = g.user_id
    data = request.get_json()
    
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({'error': 'Collection name required'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Name too long (max 100 chars)'}), 400
    
    try:
        collection_id = str(uuid.uuid4())
        result = supabase_query('collections', method='POST', data={
            'id': collection_id,
            'user_id': user_id,
            'name': name,
            'description': description,
            'cover_image': None,
            'image_count': 0,
            'created_at': datetime.utcnow().isoformat()
        }, use_service_key=True)
        
        created = result[0] if isinstance(result, list) and result else {'id': collection_id, 'name': name}
        return jsonify({'success': True, 'collection': created}), 201
        
    except Exception as e:
        logger.error(f"Create collection error: {e}")
        return jsonify({'error': 'Failed to create collection'}), 500


@collections_bp.route('/collections/<collection_id>', methods=['DELETE'])
@require_auth
def delete_collection(collection_id):
    """Delete a collection."""
    user_id = g.user_id
    try:
        supabase_query(
            f"collections?id=eq.{collection_id}&user_id=eq.{user_id}",
            method='DELETE', use_service_key=True
        )
        # Remove collection_id from images
        supabase_query(
            f"generated_images?collection_id=eq.{collection_id}&user_id=eq.{user_id}",
            method='PATCH',
            data={'collection_id': None},
            use_service_key=True
        )
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Delete collection error: {e}")
        return jsonify({'error': 'Failed to delete collection'}), 500


@collections_bp.route('/collections/<collection_id>/add', methods=['POST'])
@require_auth
def add_to_collection(collection_id):
    """Add an image to a collection."""
    user_id = g.user_id
    data = request.get_json()
    image_id = data.get('image_id')
    
    if not image_id:
        return jsonify({'error': 'Image ID required'}), 400
    
    try:
        # Verify ownership
        collections = supabase_query('collections', filters={'id': collection_id, 'user_id': user_id}, use_service_key=True)
        if not collections:
            return jsonify({'error': 'Collection not found'}), 404
        
        supabase_query(
            f"generated_images?id=eq.{image_id}&user_id=eq.{user_id}",
            method='PATCH',
            data={'collection_id': collection_id},
            use_service_key=True
        )
        
        # Update image count
        count = collections[0].get('image_count', 0) + 1
        supabase_query(
            f"collections?id=eq.{collection_id}&user_id=eq.{user_id}",
            method='PATCH',
            data={'image_count': count},
            use_service_key=True
        )
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Add to collection error: {e}")
        return jsonify({'error': 'Failed to add to collection'}), 500


@collections_bp.route('/collections/<collection_id>/remove', methods=['POST'])
@require_auth
def remove_from_collection(collection_id):
    """Remove an image from a collection."""
    user_id = g.user_id
    data = request.get_json()
    image_id = data.get('image_id')

    if not image_id:
        return jsonify({'error': 'Image ID required'}), 400

    try:
        collections = supabase_query('collections', filters={'id': collection_id, 'user_id': user_id}, use_service_key=True)
        if not collections:
            return jsonify({'error': 'Collection not found'}), 404

        supabase_query(
            f"generated_images?id=eq.{image_id}&user_id=eq.{user_id}",
            method='PATCH',
            data={'collection_id': None},
            use_service_key=True
        )

        count = max(0, collections[0].get('image_count', 0) - 1)
        supabase_query(
            f"collections?id=eq.{collection_id}&user_id=eq.{user_id}",
            method='PATCH',
            data={'image_count': count},
            use_service_key=True
        )

        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Remove from collection error: {e}")
        return jsonify({'error': 'Failed to remove image'}), 500


@collections_bp.route('/collections/<collection_id>/images', methods=['GET'])
@require_auth
def get_collection_images(collection_id):
    """Get all images in a collection."""
    user_id = g.user_id
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/generated_images?collection_id=eq.{collection_id}&user_id=eq.{user_id}&order=created_at.desc"
        response = req.get(url, headers=get_headers(use_service_key=True), timeout=10)
        images = response.json() if response.text else []
        
        return jsonify({'success': True, 'images': images if isinstance(images, list) else []}), 200
    except Exception as e:
        logger.error(f"Get collection images error: {e}")
        return jsonify({'error': 'Failed to fetch collection images'}), 500
