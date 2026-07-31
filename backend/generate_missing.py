import requests, os

BASE = 'http://localhost:5000/api'
OUTPUT = r'C:\Users\Acer\OneDrive\Documents\Default Project\arua result'

r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

missing = [
    ("04-futuristic-fashion", "Beautiful model in futuristic cyberpunk fashion, neon accents, holographic materials, perfect face with glowing details, sci-fi editorial, sharp focus", 'cyberpunk', 'fashion'),
    ("05-ethnic-fashion", "Beautiful model in traditional Indian bridal lehenga, gold embroidery, red silk, warm cinematic lighting, flawless skin, detailed eyes and jewelry, bridal editorial", 'fantasy', 'fashion'),
    ("06-winter-fashion", "Beautiful model in cozy winter fashion, chunky knit sweater, scarf, soft natural lighting, clear face with natural makeup, lifestyle photography", 'realistic', 'fashion'),
]

for filename, prompt, style, category in missing:
    print(f'[{filename}] Generating...', end=' ')
    r = requests.post(f'{BASE}/generate', json={
        'prompt': prompt,
        'negative_prompt': 'ugly face, deformed face, blurry face, bad anatomy',
        'style': style, 'category': category,
        'num_images': 1, 'quality': 'ultra', 'resolution': '4k', 'aspect_ratio': '3:4'
    }, headers=headers, timeout=120)
    if r.ok:
        images = r.json().get('images', [])
        if images:
            url = images[0]['url']
            try:
                img_data = requests.get(url, timeout=120).content
                path = os.path.join(OUTPUT, f'{filename}.png')
                with open(path, 'wb') as f:
                    f.write(img_data)
                print(f'Saved ({len(img_data)//1024} KB)')
            except Exception as e:
                print(f'Download error: {e}')
                path = os.path.join(OUTPUT, f'{filename}_url.txt')
                with open(path, 'w') as f:
                    f.write(url)
                print(f'  URL saved instead')
        else:
            print('No images')
    else:
        print(f'FAIL: {r.json()}')
    import time; time.sleep(1)

print(f'\nDone! Check {OUTPUT}')
