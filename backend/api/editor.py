"""
ARUA AI - Image Editor API
Pillow-based image editing, filters, and transformations
"""

import io
import uuid
import logging
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from utils.supabase_client import supabase_query, upload_to_storage
from utils.image_utils import (
    url_to_image, image_to_base64, image_to_bytes, base64_to_image,
    resize_image, crop_image, rotate_image, flip_image,
    adjust_brightness, adjust_contrast, adjust_saturation,
    apply_blur, apply_sharpen, apply_grayscale,
    apply_vintage_filter, apply_hdr_filter, apply_neon_glow,
    apply_cartoon_filter, apply_sketch_filter,
    remove_background, upscale_image
)

logger = logging.getLogger(__name__)
editor_bp = Blueprint('editor', __name__)


@editor_bp.route('/editor/edit', methods=['POST'])
@require_auth
def apply_edits():
    """Apply multiple edits to an image."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    image_url = data.get('image_url')
    image_b64 = data.get('image_base64')
    edits = data.get('edits', {})
    save_version = data.get('save_version', True)
    original_image_id = data.get('image_id')
    
    if not image_url and not image_b64:
        return jsonify({'error': 'Image URL or base64 required'}), 400
    
    try:
        # Load image
        if image_b64:
            image = base64_to_image(image_b64)
        else:
            image = url_to_image(image_url)
        
        # Apply edits
        for edit_type, value in edits.items():
            try:
                if edit_type == 'brightness' and float(value) != 1.0:
                    image = adjust_brightness(image, float(value))
                elif edit_type == 'contrast' and float(value) != 1.0:
                    image = adjust_contrast(image, float(value))
                elif edit_type == 'saturation' and float(value) != 1.0:
                    image = adjust_saturation(image, float(value))
                elif edit_type == 'blur' and float(value) > 0:
                    image = apply_blur(image, float(value))
                elif edit_type == 'sharpen' and float(value) > 0:
                    image = apply_sharpen(image, float(value))
                elif edit_type == 'filter':
                    filter_map = {
                        'grayscale': apply_grayscale,
                        'vintage': apply_vintage_filter,
                        'hdr': apply_hdr_filter,
                        'neon': apply_neon_glow,
                        'cartoon': apply_cartoon_filter,
                        'sketch': apply_sketch_filter
                    }
                    if value in filter_map:
                        image = filter_map[value](image)
                elif edit_type == 'rotate' and float(value) != 0:
                    image = rotate_image(image, float(value))
                elif edit_type == 'flip':
                    image = flip_image(image, str(value))
                elif edit_type == 'resize':
                    w = int(value.get('width', image.width))
                    h = int(value.get('height', image.height))
                    image = resize_image(image, w, h, maintain_aspect=value.get('maintain_aspect', True))
                elif edit_type == 'crop':
                    image = crop_image(image, int(value['x']), int(value['y']), int(value['width']), int(value['height']))
            except Exception as edit_error:
                logger.warning(f"Edit {edit_type} failed: {edit_error}")
                continue
        
        # Convert result to base64
        result_b64 = image_to_base64(image)
        
        # Optionally save as new version
        version_id = None
        if save_version and original_image_id:
            user_id = g.user_id
            version_id = str(uuid.uuid4())
            try:
                supabase_query('image_versions', method='POST', data={
                    'id': version_id,
                    'original_image_id': original_image_id,
                    'user_id': user_id,
                    'edits_applied': edits,
                    'created_at': datetime.utcnow().isoformat()
                }, use_service_key=True)
            except Exception as ver_err:
                logger.warning(f"Version save failed: {ver_err}")
        
        return jsonify({
            'success': True,
            'edited_image': f"data:image/png;base64,{result_b64}",
            'version_id': version_id,
            'dimensions': {'width': image.width, 'height': image.height}
        }), 200
        
    except Exception as e:
        logger.error(f"Image edit error: {e}")
        return jsonify({'error': 'Image editing failed', 'message': str(e)}), 500


@editor_bp.route('/editor/remove-background', methods=['POST'])
@require_auth
def remove_bg():
    """Remove image background."""
    data = request.get_json()
    image_url = data.get('image_url')
    image_b64 = data.get('image_base64')
    
    if not image_url and not image_b64:
        return jsonify({'error': 'Image required'}), 400
    
    try:
        image = base64_to_image(image_b64) if image_b64 else url_to_image(image_url)
        result = remove_background(image)
        result_b64 = image_to_base64(result)
        
        return jsonify({
            'success': True,
            'result': f"data:image/png;base64,{result_b64}"
        }), 200
    except Exception as e:
        logger.error(f"BG removal error: {e}")
        return jsonify({'error': 'Background removal failed'}), 500


@editor_bp.route('/editor/upscale', methods=['POST'])
@require_auth
def upscale():
    """Upscale an image."""
    data = request.get_json()
    image_url = data.get('image_url')
    image_b64 = data.get('image_base64')
    scale = min(int(data.get('scale', 2)), 4)  # Max 4x
    
    if not image_url and not image_b64:
        return jsonify({'error': 'Image required'}), 400
    
    try:
        image = base64_to_image(image_b64) if image_b64 else url_to_image(image_url)
        result = upscale_image(image, scale)
        result_b64 = image_to_base64(result)
        
        return jsonify({
            'success': True,
            'result': f"data:image/png;base64,{result_b64}",
            'new_dimensions': {'width': result.width, 'height': result.height}
        }), 200
    except Exception as e:
        logger.error(f"Upscale error: {e}")
        return jsonify({'error': 'Upscale failed'}), 500


@editor_bp.route('/editor/versions/<image_id>', methods=['GET'])
@require_auth
def get_versions(image_id):
    """Get all versions of an image."""
    user_id = g.user_id
    try:
        from utils.supabase_client import SUPABASE_URL, get_headers
        import requests as req
        
        url = f"{SUPABASE_URL}/rest/v1/image_versions?original_image_id=eq.{image_id}&user_id=eq.{user_id}&order=created_at.desc"
        response = req.get(url, headers=get_headers(use_service_key=True), timeout=10)
        versions = response.json() if response.text else []
        
        return jsonify({'success': True, 'versions': versions if isinstance(versions, list) else []}), 200
    except Exception as e:
        logger.error(f"Get versions error: {e}")
        return jsonify({'error': 'Failed to fetch versions'}), 500
