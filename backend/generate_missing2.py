import requests, os

BASE = 'http://localhost:5000/api'
OUTPUT = r'C:\Users\Acer\OneDrive\Documents\Default Project\arua result'

r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

missing = [
    ("04-futuristic-fashion", "Beautiful model in futuristic cyberpunk fashion, neon accents, holographic materials, perfect face with glowing details, sci-fi editorial, sharp focus", 'cyberpunk'),
    ("05-ethnic-fashion", "Beautiful model in traditional Indian bridal lehenga, gold embroidery, red silk, warm cinematic lighting, flawless skin, detailed eyes and jewelry, bridal editorial", 'fantasy'),
    ("06-winter-fashion", "Beautiful model in cozy winter fashion, chunky knit sweater, scarf, soft natural lighting, clear face with natural makeup, lifestyle photography", 'realistic'),
]

for filename, prompt, style in missing:
    print(f'[{filename}] Generating...', end=' ')
    r = requests.post(f'{BASE}/generate', json={
        'prompt': prompt,
        'negative_prompt': 'ugly face, deformed face, blurry face, bad anatomy',
        'style': style, 'category': 'fashion',
        'num_images': 1, 'quality': 'ultra', 'resolution': '4k', 'aspect_ratio': '3:4'
    }, headers=headers, timeout=120)
    if r.ok:
        images = r.json().get('images', [])
        if images:
            url = images[0]['url']
            print(f'\n  URL: {url}')
            # Save URL to text file instead of downloading
            path = os.path.join(OUTPUT, f'{filename}.txt')
            with open(path, 'w') as f:
                f.write(url)
            print(f'  URL saved to {filename}.txt')
            # Try to dl with longer timeout
            try:
                img_data = requests.get(url, timeout=180, headers={'User-Agent': 'Mozilla/5.0'}).content
                if len(img_data) > 10000:
                    png_path = os.path.join(OUTPUT, f'{filename}.png')
                    with open(png_path, 'wb') as f:
                        f.write(img_data)
                    print(f'  Image downloaded: {len(img_data)//1024} KB')
                else:
                    print(f'  Response too small ({len(img_data)} bytes), URL saved instead')
            except Exception as e:
                print(f'  Download failed: {e}')
        else:
            print('No images')
    else:
        print(f'FAIL: {r.json()}')
    import time; time.sleep(1)

print(f'\nDone! Check {OUTPUT}')
