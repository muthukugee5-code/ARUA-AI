"""
AURA AI - Video Creation API
Generates scene images for AI videos (Ken Burns slideshow rendered client-side)
"""

import os
import re
import uuid
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, rate_limit
from utils.credits import check_and_refill_credits
from utils.supabase_client import supabase_query
from api.generate import build_generation_url, enhance_prompt_with_hf, get_dimensions

logger = logging.getLogger(__name__)
video_bp = Blueprint('video', __name__)

# Credits per scene (each scene is a generated image)
CREDITS_PER_SCENE = 15
MAX_SCENES = 8
MAX_DURATION = 10  # seconds per scene


@video_bp.route('/video/create', methods=['POST'])
@require_auth
@rate_limit(max_requests=15, window=60)
def create_video():
    """Generate scene images for an AI video."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'JSON body required'}), 400

    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Validation error', 'message': 'Prompt is required'}), 400

    if len(prompt) > 1000:
        return jsonify({'error': 'Validation error', 'message': 'Prompt too long (max 1000 chars)'}), 400

    style = data.get('style', 'cinematic')
    category = data.get('category', '')
    aspect_ratio = data.get('aspect_ratio', '16:9')
    resolution = data.get('resolution', 'hd')
    num_scenes = min(max(int(data.get('num_scenes', 3)), 2), MAX_SCENES)
    scene_duration = min(max(float(data.get('scene_duration', 3)), 1), MAX_DURATION)
    enhance = data.get('enhance_prompt', True)
    model = data.get('model', 'flux')

    user_id = g.user_id

    try:
        check_and_refill_credits(user_id)

        profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
        profile = profiles[0] if profiles else {}
        credits = profile.get('ai_credits', 0)

        credits_needed = num_scenes * CREDITS_PER_SCENE
        if credits < credits_needed:
            return jsonify({
                'error': 'Insufficient credits',
                'message': f'You need {credits_needed} credits but have {credits}. Please upgrade your plan.'
            }), 402

        final_prompt = enhance_prompt_with_hf(prompt, style, category) if enhance else prompt

        width, height = get_dimensions(aspect_ratio, resolution)

        scenes = []
        for i in range(num_scenes):
            seed = uuid.uuid4().int % 1000000
            scene_prompt = final_prompt if num_scenes == 1 else (
                f"{final_prompt}, scene {i + 1} of {num_scenes}, {variation_phrase(i)}"
            )
            scenes.append({
                'index': i,
                'seed': seed,
                'url': build_generation_url(scene_prompt, width, height, seed=seed, model=model),
                'duration': scene_duration
            })

        video_id = str(uuid.uuid4())

        try:
            supabase_query('videos', method='POST', data={
                'id': video_id,
                'user_id': user_id,
                'prompt': prompt,
                'enhanced_prompt': final_prompt,
                'style': style,
                'category': category,
                'aspect_ratio': aspect_ratio,
                'resolution': resolution,
                'num_scenes': num_scenes,
                'scene_duration': scene_duration,
                'scene_images': scenes,
                'model': model,
                'created_at': datetime.utcnow().isoformat()
            }, use_service_key=True)
        except Exception as db_err:
            logger.warning(f"Failed to save video record: {db_err}")

        try:
            new_credits = max(0, credits - credits_needed)
            new_total = profile.get('total_generated', 0) + num_scenes
            supabase_query(
                f"profiles?user_id=eq.{user_id}",
                method='PATCH',
                data={'ai_credits': new_credits, 'total_generated': new_total},
                use_service_key=True
            )
        except Exception as e:
            logger.warning(f"Credit deduction failed: {e}")

        try:
            supabase_query('activity_logs', method='POST', data={
                'user_id': user_id,
                'action': 'create_video',
                'details': f"Created {num_scenes}-scene video: {prompt[:100]}",
                'created_at': datetime.utcnow().isoformat()
            }, use_service_key=True)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'video': {
                'id': video_id,
                'prompt': prompt,
                'enhanced_prompt': final_prompt,
                'scenes': scenes,
                'num_scenes': num_scenes,
                'scene_duration': scene_duration,
                'aspect_ratio': aspect_ratio,
                'width': width,
                'height': height
            },
            'credits_used': credits_needed,
            'credits_remaining': max(0, credits - credits_needed)
        }), 200

    except Exception as e:
        logger.error(f"Video creation error: {e}")
        return jsonify({'error': 'Video creation failed', 'message': str(e)}), 500


@video_bp.route('/videos', methods=['GET'])
@require_auth
def get_videos():
    """Get user's video history."""
    user_id = g.user_id
    try:
        videos = supabase_query(
            'videos',
            filters={'user_id': user_id},
            use_service_key=True
        )
        videos = videos if isinstance(videos, list) else []
        videos.sort(key=lambda v: v.get('created_at', ''), reverse=True)
        return jsonify({'success': True, 'videos': videos}), 200
    except Exception as e:
        logger.warning(f"Video history fetch failed: {e}")
        return jsonify({'success': True, 'videos': []}), 200


def variation_phrase(index):
    """Create a variation phrase for scene diversity."""
    phrases = [
        'different angle, establishing shot',
        'close-up detail shot',
        'wide cinematic shot',
        'dramatic low angle',
        'overhead aerial view',
        'dynamic action shot',
        'beautiful landscape view',
        'intimate portrait shot'
    ]
    return phrases[index % len(phrases)]
