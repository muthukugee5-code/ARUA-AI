"""
ARUA AI - Image Generation API
Pollinations.ai integration with prompt enhancement
"""

import os
import re
import uuid
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, rate_limit
from utils.credits import check_and_refill_credits
from utils.supabase_client import supabase_query, upload_to_storage

logger = logging.getLogger(__name__)
generate_bp = Blueprint('generate', __name__)

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

# Style mappings for Pollinations.ai
STYLE_PROMPTS = {
    'realistic': 'photorealistic, highly detailed, 8k, professional photography',
    'hyper_realistic': 'hyperrealistic, photorealistic, ultra detailed, 16k, studio lighting, award winning photography',
    'anime': 'anime style, vibrant colors, detailed anime art, Studio Ghibli quality',
    'manga': 'manga style, black and white, detailed line art, professional manga',
    'pixar': 'Pixar 3D animation style, colorful, charming, high quality CGI',
    'disney': 'Disney animation style, magical, colorful, expressive characters',
    'cartoon': 'cartoon style, vibrant colors, clean lines, professional illustration',
    'watercolor': 'watercolor painting, soft washes, artistic, textured paper',
    'oil_painting': 'oil painting, textured canvas, classical art style, museum quality',
    'pencil_sketch': 'pencil sketch, detailed line drawing, graphite, shading, artistic',
    'digital_painting': 'digital painting, concept art, professional digital art, detailed',
    'pixel_art': 'pixel art, 16-bit style, retro game art, clean pixels',
    'fantasy': 'fantasy art, magical, ethereal, detailed fantasy illustration',
    'cyberpunk': 'cyberpunk, neon lights, futuristic city, dark aesthetic, sci-fi',
    'sci_fi': 'science fiction, futuristic, space, advanced technology, cinematic',
    'gothic': 'gothic art style, dark, dramatic, Victorian, ornate details',
    'hdr': 'HDR photography, high dynamic range, vivid colors, dramatic lighting',
    'cinematic': 'cinematic photography, film grain, dramatic lighting, movie poster quality',
    'clay': 'clay render, 3D, smooth surfaces, colorful, cute clay art style',
    'low_poly': 'low poly 3D art, geometric, angular, minimalist, clean',
    'isometric': 'isometric 3D illustration, clean, colorful, detailed isometric view',
    'luxury': 'luxury aesthetic, premium, elegant, sophisticated, high-end photography',
    'minimal': 'minimalist design, clean, simple, white background, elegant',
    'photorealistic': 'photorealistic, ultra detailed, professional photography, 8k resolution',
    'concept_art': 'concept art, professional illustration, detailed, artistic, game art quality'
}

# Category-specific prompt enhancers
CATEGORY_PROMPTS = {
    'ui_mobile': 'mobile app UI design, clean interface, modern design system, iOS/Android style',
    'ui_web': 'web UI design, modern website design, clean layout, professional web design',
    'ui_dashboard': 'dashboard UI design, data visualization, clean admin panel, modern SaaS',
    'logo': 'logo design, vector style, clean, professional branding, white background',
    'poster': 'poster design, professional print design, typography, graphic design',
    'banner': 'banner design, professional marketing banner, clean layout',
    'social_media': 'social media post design, Instagram-ready, vibrant, modern',
    'thumbnail': 'YouTube thumbnail, eye-catching, bold text, high contrast, clickbait style',
    '3d_character': '3D character design, game ready, detailed textures, Blender render quality',
    '3d_product': '3D product visualization, studio lighting, commercial photography style',
    'anime_character': 'detailed anime character, full body, expressive, vibrant colors',
    'architecture': 'architectural visualization, photorealistic render, modern architecture',
    'interior': 'interior design visualization, photorealistic, elegant, modern interior',
    'fashion': 'fashion photography, editorial style, beautiful face, perfect skin, detailed eyes, professional studio lighting, sharp focus on face',
    'product_mockup': 'product mockup, clean white background, professional commercial photography'
}


def build_generation_url(prompt, width=1024, height=1024, seed=None, model='flux'):
    """Build Pollinations.ai generation URL."""
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_BASE}/{encoded_prompt}"
    params = [f"width={width}", f"height={height}", f"model={model}", "nologo=true"]
    if seed and seed > 0:
        params.append(f"seed={seed}")
    return url + '?' + '&'.join(params)


def enhance_prompt_with_hf(prompt, style=None, category=None):
    """Enhance prompt using Hugging Face API."""
    if not HUGGINGFACE_API_KEY:
        return enhance_prompt_local(prompt, style, category)
    
    system_message = """You are an expert AI image prompt engineer. 
    Enhance the given prompt to create stunning, detailed AI-generated images. 
    Add specific details about lighting, composition, color, style, and technical quality.
    Keep response to ONE enhanced prompt only, no explanations."""
    
    style_hint = f" in {style} style" if style else ""
    category_hint = f" for {category}" if category else ""
    
    user_message = f"Enhance this prompt{style_hint}{category_hint}: '{prompt}'"
    
    headers = {
        'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "inputs": f"<s>[INST] {system_message}\n\n{user_message} [/INST]",
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                enhanced = result[0].get('generated_text', prompt).strip()
                # Clean up the response
                enhanced = enhanced.split('[/INST]')[-1].strip()
                enhanced = enhanced.replace('<s>', '').replace('</s>', '').strip()
                return enhanced if enhanced else prompt
    except Exception as e:
        logger.warning(f"HuggingFace API error: {e}")
    
    return enhance_prompt_local(prompt, style, category)


def enhance_prompt_local(prompt, style=None, category=None):
    """Local prompt enhancement without external API."""
    enhancements = []
    
    # Style-specific additions
    if style and style in STYLE_PROMPTS:
        enhancements.append(STYLE_PROMPTS[style])
    
    # Category-specific additions
    if category and category in CATEGORY_PROMPTS:
        enhancements.append(CATEGORY_PROMPTS[category])
    
    # General quality boosts
    quality_keywords = [
        "highly detailed", "professional quality", "masterpiece",
        "sharp focus", "8k resolution", "beautiful composition",
        "perfect lighting", "award winning"
    ]
    enhancements.extend(quality_keywords[:3])
    
    if enhancements:
        return f"{prompt}, {', '.join(enhancements)}"
    return prompt


def get_dimensions(aspect_ratio, resolution='hd'):
    """Get image dimensions from aspect ratio and resolution."""
    base_sizes = {
        'sd': 512, 'hd': 1024, '4k': 2048
    }
    base = base_sizes.get(resolution, 1024)
    
    ratios = {
        '1:1': (base, base),
        '16:9': (base, int(base * 9 / 16)),
        '9:16': (int(base * 9 / 16), base),
        '4:3': (base, int(base * 3 / 4)),
        '3:4': (int(base * 3 / 4), base),
        '3:2': (base, int(base * 2 / 3)),
        '2:3': (int(base * 2 / 3), base),
        '21:9': (base, int(base * 9 / 21))
    }
    
    return ratios.get(aspect_ratio, (base, base))


@generate_bp.route('/generate', methods=['POST'])
@require_auth
@rate_limit(max_requests=30, window=60)
def generate_image():
    """Generate AI images using Pollinations.ai."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'JSON body required'}), 400
    
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Validation error', 'message': 'Prompt is required'}), 400
    
    if len(prompt) > 1000:
        return jsonify({'error': 'Validation error', 'message': 'Prompt too long (max 1000 chars)'}), 400
    
    # Generation parameters
    negative_prompt = data.get('negative_prompt', '')
    style = data.get('style', 'realistic')
    category = data.get('category', '')
    aspect_ratio = data.get('aspect_ratio', '1:1')
    resolution = data.get('resolution', 'hd')
    quality = data.get('quality', 'high')
    num_images = min(int(data.get('num_images', 1)), 4)  # Max 4 images
    seed = data.get('seed', -1)
    enhance = data.get('enhance_prompt', True)
    model = data.get('model', 'flux')
    
    user_id = g.user_id
    
    try:
        # Auto-refill credits if 24h passed
        check_and_refill_credits(user_id)

        # Check user credits
        profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
        profile = profiles[0] if profiles else {}
        credits = profile.get('ai_credits', 0)
        
        credits_needed = num_images * 15
        if credits < credits_needed:
            return jsonify({
                'error': 'Insufficient credits',
                'message': f'You need {credits_needed} credits but have {credits}. Please upgrade your plan.'
            }), 402
        
        # Build enhanced prompt
        final_prompt = enhance_prompt_with_hf(prompt, style, category) if enhance else prompt
        
        # Add style keywords
        if style in STYLE_PROMPTS and style not in final_prompt:
            final_prompt = f"{final_prompt}, {STYLE_PROMPTS[style]}"
        
        # Add quality modifiers
        if quality == 'ultra':
            final_prompt += ", ultra high quality, masterpiece, perfect details"
        elif quality == 'high':
            final_prompt += ", high quality, detailed"
        
        # Add negative prompt handling (as part of prompt for Pollinations)
        if negative_prompt:
            final_prompt += f" | Avoid: {negative_prompt}"
        
        # Get dimensions
        width, height = get_dimensions(aspect_ratio, resolution)
        
        # Generate images
        generated_images = []
        
        for i in range(num_images):
            image_seed = seed if seed > 0 else (uuid.uuid4().int % 1000000)
            
            # Build URL
            img_url = build_generation_url(
                final_prompt, width, height,
                seed=image_seed, model=model
            )
            
            image_id = str(uuid.uuid4())
            
            # Save generation record to database
            try:
                record = supabase_query('generated_images', method='POST', data={
                    'id': image_id,
                    'user_id': user_id,
                    'prompt': prompt,
                    'enhanced_prompt': final_prompt,
                    'negative_prompt': negative_prompt,
                    'style': style,
                    'category': category,
                    'aspect_ratio': aspect_ratio,
                    'resolution': resolution,
                    'width': width,
                    'height': height,
                    'seed': image_seed,
                    'model': model,
                    'image_url': img_url,
                    'is_favorite': False,
                    'is_public': False,
                    'downloads': 0,
                    'created_at': datetime.utcnow().isoformat()
                }, use_service_key=True)
            except Exception as db_err:
                logger.warning(f"Failed to save image record: {db_err}")
            
            generated_images.append({
                'id': image_id,
                'url': img_url,
                'seed': image_seed,
                'width': width,
                'height': height
            })
        
        # Deduct credits
        try:
            new_credits = max(0, credits - credits_needed)
            new_total = profile.get('total_generated', 0) + num_images
            supabase_query(
                f"profiles?user_id=eq.{user_id}",
                method='PATCH',
                data={
                    'ai_credits': new_credits,
                    'total_generated': new_total
                },
                use_service_key=True
            )
        except Exception as e:
            logger.warning(f"Credit deduction failed: {e}")
        
        # Log activity
        try:
            supabase_query('activity_logs', method='POST', data={
                'user_id': user_id,
                'action': 'generate_image',
                'details': f"Generated {num_images} {style} image(s): {prompt[:100]}",
                'created_at': datetime.utcnow().isoformat()
            }, use_service_key=True)
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'images': generated_images,
            'enhanced_prompt': final_prompt,
            'original_prompt': prompt,
            'credits_used': credits_needed,
            'credits_remaining': max(0, credits - credits_needed)
        }), 200
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': 'Generation failed', 'message': str(e)}), 500


@generate_bp.route('/enhance-prompt', methods=['POST'])
@require_auth
@rate_limit(max_requests=20, window=60)
def enhance_prompt_route():
    """Enhance a user's prompt using AI."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    prompt = data.get('prompt', '').strip()
    style = data.get('style')
    category = data.get('category')
    
    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400
    
    try:
        enhanced = enhance_prompt_with_hf(prompt, style, category)
        
        # Save to prompt history
        try:
            supabase_query('prompt_history', method='POST', data={
                'user_id': g.user_id,
                'original_prompt': prompt,
                'enhanced_prompt': enhanced,
                'style': style,
                'category': category,
                'created_at': datetime.utcnow().isoformat()
            }, use_service_key=True)
        except Exception:
            pass
        
        # Generate smart suggestions
        suggestions = generate_prompt_suggestions(prompt)
        
        return jsonify({
            'success': True,
            'original': prompt,
            'enhanced': enhanced,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Prompt enhancement error: {e}")
        return jsonify({'error': 'Enhancement failed'}), 500


def generate_prompt_suggestions(prompt):
    """Generate contextual prompt improvement suggestions."""
    suggestions = []
    
    lighting_keywords = ['lighting', 'light', 'shadow', 'illuminat']
    if not any(k in prompt.lower() for k in lighting_keywords):
        suggestions.append({
            'type': 'lighting',
            'icon': '💡',
            'text': 'Add lighting details',
            'addition': 'dramatic studio lighting, golden hour'
        })
    
    camera_keywords = ['camera', 'lens', 'angle', 'shot', 'close-up', 'portrait', 'wide']
    if not any(k in prompt.lower() for k in camera_keywords):
        suggestions.append({
            'type': 'camera',
            'icon': '📷',
            'text': 'Add camera perspective',
            'addition': 'shot on Canon 5D, 85mm lens, shallow depth of field'
        })
    
    quality_keywords = ['4k', '8k', 'hd', 'detailed', 'sharp', 'quality']
    if not any(k in prompt.lower() for k in quality_keywords):
        suggestions.append({
            'type': 'quality',
            'icon': '✨',
            'text': 'Add quality keywords',
            'addition': '8K resolution, highly detailed, sharp focus'
        })
    
    color_keywords = ['color', 'palette', 'tone', 'hue', 'vibrant', 'muted']
    if not any(k in prompt.lower() for k in color_keywords):
        suggestions.append({
            'type': 'color',
            'icon': '🎨',
            'text': 'Specify color palette',
            'addition': 'vibrant colors, rich color palette, complementary colors'
        })
    
    suggestions.append({
        'type': 'composition',
        'icon': '🖼️',
        'text': 'Enhance composition',
        'addition': 'rule of thirds, balanced composition, professional framing'
    })
    
    return suggestions[:4]
