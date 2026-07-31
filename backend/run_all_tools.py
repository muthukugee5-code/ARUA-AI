"""
ARUA AI - Full Tools Test
Generates, edits, upscales, removes background, and saves all results
"""

import os, json, requests, base64, io
from PIL import Image
from datetime import datetime

BASE = 'http://localhost:5000/api'
OUTPUT = r'C:\Users\Acer\OneDrive\Documents\Default Project\arua result'
os.makedirs(OUTPUT, exist_ok=True)

print(f"Saving results to: {OUTPUT}")

# Login
r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
data = r.json()
token = data['access_token']
headers = {'Authorization': f'Bearer {token}'}
print('[1] Login OK')

# 1. Enhance Prompt
print('\n--- 1. Prompt Enhancement ---')
r = requests.post(f'{BASE}/enhance-prompt', json={
    'prompt': 'a majestic dragon flying over a futuristic cyberpunk city at sunset',
    'style': 'cyberpunk',
    'category': 'general'
}, headers=headers)
if r.ok:
    enhanced = r.json().get('enhanced', '')
    with open(os.path.join(OUTPUT, '01-enhanced-prompt.txt'), 'w') as f:
        f.write(f"Original: a majestic dragon flying over a futuristic cyberpunk city at sunset\n\nEnhanced: {enhanced}")
    print(f'  Enhanced prompt saved ({len(enhanced)} chars)')

# 2. Generate Image (standard quality)
print('\n--- 2. Image Generation ---')
r = requests.post(f'{BASE}/generate', json={
    'prompt': 'a majestic dragon flying over a futuristic cyberpunk city at sunset, cinematic lighting, epic',
    'style': 'cyberpunk',
    'category': 'general',
    'num_images': 1,
    'quality': 'standard',
    'aspect_ratio': '1:1',
    'enhance_prompt': False
}, headers=headers)

generated_url = None
if r.ok:
    d = r.json()
    images = d.get('images', [])
    print(f'  Generated {len(images)} images, credits remaining: {d.get("credits_remaining")}')
    if images:
        generated_url = images[0]['url']
        r_img = requests.get(generated_url, timeout=30)
        if r_img.ok:
            path = os.path.join(OUTPUT, '02-generated-image.png')
            with open(path, 'wb') as f:
                f.write(r_img.content)
            print(f'  Saved to: 02-generated-image.png ({len(r_img.content)} bytes)')
else:
    print(f'  FAIL: {r.json()}')

# 3. Editor - Edit (brightness + contrast + filter)
print('\n--- 3. Editor - Edit (brightness, contrast, vintage filter) ---')
if generated_url:
    r = requests.post(f'{BASE}/editor/edit', json={
        'image_url': generated_url,
        'edits': {
            'brightness': 1.2,
            'contrast': 1.15,
            'saturation': 1.1,
            'filter': 'vintage'
        }
    }, headers=headers)
    if r.ok:
        result_b64 = r.json().get('edited_image', '')
        if result_b64 and result_b64.startswith('data:image'):
            img_data = base64.b64decode(result_b64.split(',')[1])
            path = os.path.join(OUTPUT, '03-edited-vintage.png')
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f'  Saved to: 03-edited-vintage.png ({len(img_data)} bytes)')

# 4. Editor - Neon Glow Filter
print('\n--- 4. Editor - Neon Glow Filter ---')
if generated_url:
    r = requests.post(f'{BASE}/editor/edit', json={
        'image_url': generated_url,
        'edits': {'filter': 'neon'}
    }, headers=headers)
    if r.ok:
        result_b64 = r.json().get('edited_image', '')
        if result_b64 and result_b64.startswith('data:image'):
            img_data = base64.b64decode(result_b64.split(',')[1])
            path = os.path.join(OUTPUT, '04-edited-neon.png')
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f'  Saved to: 04-edited-neon.png ({len(img_data)} bytes)')

# 5. Editor - Sketch Filter
print('\n--- 5. Editor - Sketch Filter ---')
if generated_url:
    r = requests.post(f'{BASE}/editor/edit', json={
        'image_url': generated_url,
        'edits': {'filter': 'sketch'}
    }, headers=headers)
    if r.ok:
        result_b64 = r.json().get('edited_image', '')
        if result_b64 and result_b64.startswith('data:image'):
            img_data = base64.b64decode(result_b64.split(',')[1])
            path = os.path.join(OUTPUT, '05-edited-sketch.png')
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f'  Saved to: 05-edited-sketch.png ({len(img_data)} bytes)')

# 6. Editor - Upscale 2x
print('\n--- 6. Editor - Upscale (2x) ---')
if generated_url:
    r = requests.post(f'{BASE}/editor/upscale', json={
        'image_url': generated_url,
        'scale': 2
    }, headers=headers)
    if r.ok:
        d = r.json()
        dims = d.get('new_dimensions', {})
        result_b64 = d.get('result', '')
        if result_b64 and result_b64.startswith('data:image'):
            img_data = base64.b64decode(result_b64.split(',')[1])
            path = os.path.join(OUTPUT, '06-upscaled-2x.png')
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f'  Saved to: 06-upscaled-2x.png ({dims.get("width")}x{dims.get("height")}, {len(img_data)} bytes)')

# 7. Editor - Upscale 4x
print('\n--- 7. Editor - Upscale (4x) ---')
if generated_url:
    r = requests.post(f'{BASE}/editor/upscale', json={
        'image_url': generated_url,
        'scale': 4
    }, headers=headers)
    if r.ok:
        d = r.json()
        dims = d.get('new_dimensions', {})
        result_b64 = d.get('result', '')
        if result_b64 and result_b64.startswith('data:image'):
            img_data = base64.b64decode(result_b64.split(',')[1])
            path = os.path.join(OUTPUT, '07-upscaled-4x.png')
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f'  Saved to: 07-upscaled-4x.png ({dims.get("width")}x{dims.get("height")}, {len(img_data)} bytes)')

# 8. Editor - Remove Background
print('\n--- 8. Editor - Remove Background ---')
if generated_url:
    r = requests.post(f'{BASE}/editor/remove-background', json={
        'image_url': generated_url
    }, headers=headers)
    if r.ok:
        result_b64 = r.json().get('result', '')
        if result_b64 and result_b64.startswith('data:image'):
            img_data = base64.b64decode(result_b64.split(',')[1])
            path = os.path.join(OUTPUT, '08-removed-bg.png')
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f'  Saved to: 08-removed-bg.png ({len(img_data)} bytes)')

# Summary
files = [f for f in os.listdir(OUTPUT) if f.endswith(('.png', '.txt'))]
print(f'\n{"="*50}')
print(f'All results saved to: {OUTPUT}')
print(f'Files created ({len(files)}):')
for f in sorted(files):
    size = os.path.getsize(os.path.join(OUTPUT, f))
    print(f'  {f} ({size//1024} KB)')
print(f'{"="*50}')
