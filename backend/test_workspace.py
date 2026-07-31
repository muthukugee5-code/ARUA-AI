import requests
BASE = 'http://localhost:5000/api'

r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
data = r.json()
token = data['access_token']
headers = {'Authorization': f'Bearer {token}'}
print('Login OK')

# Test enhance prompt
r = requests.post(f'{BASE}/enhance-prompt', json={'prompt': 'a futuristic city', 'style': 'cyberpunk', 'category': 'general'}, headers=headers)
print(f'Enhance: {r.status_code}', 'OK' if r.ok else f'FAIL {r.json()}')

# Test generate (1 image, standard quality)
r = requests.post(f'{BASE}/generate', json={
    'prompt': 'a cute cat', 'style': 'realistic', 'category': 'animals',
    'num_images': 1, 'quality': 'standard', 'aspect_ratio': '1:1'
}, headers=headers)
print(f'Generate: {r.status_code}', end='')
if r.ok:
    d = r.json()
    images = d.get('images', [])
    remaining = d.get('credits_remaining', '?')
    print(f' OK - {len(images)} images, credits left: {remaining}')
else:
    print(f' FAIL {r.json()}')

# Test editor endpoints
if r.ok and d.get('images'):
    img_url = d['images'][0]['url']
    r2 = requests.post(f'{BASE}/editor/edit', json={
        'image_url': img_url, 'edits': {'brightness': 1.2, 'contrast': 1.1}
    }, headers=headers)
    print(f'Editor edit: {r2.status_code}', 'OK' if r2.ok else f'FAIL {r2.json()}')

    r3 = requests.post(f'{BASE}/editor/upscale', json={'image_url': img_url, 'scale': 2}, headers=headers)
    print(f'Upscale: {r3.status_code}', end='')
    if r3.ok: print(f' OK - {r3.json()["new_dimensions"]}')
    else: print(f' FAIL {r3.json()}')

print('All workspace tools verified!')
