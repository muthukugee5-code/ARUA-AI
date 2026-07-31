import requests, os, time

BASE = 'http://localhost:5000/api'
OUTPUT = r'C:\Users\Acer\OneDrive\Documents\Default Project\arua result'

r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

items = [
    ("02-casual-outfit", "Beautiful model wearing modern streetwear outfit, oversized hoodie with cargo pants, urban setting, golden hour glow, clear face, natural beauty, editorial", 'realistic'),
    ("03-luxury-dress", "Elegant model in luxury silk dress with embroidery, soft studio lighting, perfect complexion, detailed facial features, high-end fashion editorial", 'luxury'),
]

for filename, prompt, style in items:
    print(f'[{filename}]...', end=' ')
    r = requests.post(f'{BASE}/generate', json={
        'prompt': prompt, 'style': style, 'category': 'fashion',
        'num_images': 1, 'quality': 'ultra', 'resolution': '4k', 'aspect_ratio': '3:4'
    }, headers=headers, timeout=120)
    if r.ok:
        images = r.json().get('images', [])
        if images:
            url = images[0]['url']
            try:
                img_data = requests.get(url, timeout=180, headers={'User-Agent': 'Mozilla/5.0'}).content
                if len(img_data) > 10000:
                    with open(os.path.join(OUTPUT, f'{filename}.png'), 'wb') as f:
                        f.write(img_data)
                    print(f'{len(img_data)//1024} KB')
                else:
                    print('small response, retrying...')
                    time.sleep(2)
                    img_data = requests.get(url, timeout=180).content
                    with open(os.path.join(OUTPUT, f'{filename}.png'), 'wb') as f:
                        f.write(img_data)
                    print(f'{len(img_data)//1024} KB')
            except Exception as e:
                print(f'dl error: {e}')
        else:
            print('no images')
    else:
        print(f'FAIL: {r.json()}')
    time.sleep(1)

print('Done')
