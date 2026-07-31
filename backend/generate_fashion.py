import requests, os, time

BASE = 'http://localhost:5000/api'
OUTPUT = r'C:\Users\Acer\OneDrive\Documents\Default Project\arua result'
os.makedirs(OUTPUT, exist_ok=True)

r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

fashion_prompts = [
    ("01-fashion-model", "Beautiful fashion model with flawless face, stunning red evening gown with sequins, walking runway, dramatic studio lighting, perfect skin, detailed eyes, sharp focus", 'hyper_realistic', 'fashion'),
    ("02-casual-outfit", "Beautiful model wearing modern streetwear outfit, oversized hoodie with cargo pants, urban setting, golden hour glow, clear face, natural beauty, editorial", 'realistic', 'fashion'),
    ("03-luxury-dress", "Elegant model in luxury silk dress with embroidery, soft studio lighting, perfect complexion, detailed facial features, high-end fashion editorial", 'luxury', 'fashion'),
    ("04-futuristic-fashion", "Beautiful model in futuristic cyberpunk fashion, neon accents, holographic materials, perfect face with glowing details, sci-fi editorial, sharp focus", 'cyberpunk', 'fashion'),
    ("05-ethnic-fashion", "Beautiful model in traditional Indian bridal lehenga, gold embroidery, red silk, warm cinematic lighting, flawless skin, detailed eyes and jewelry, bridal editorial", 'fantasy', 'fashion'),
    ("06-winter-fashion", "Beautiful model in cozy winter fashion, chunky knit sweater, scarf, soft natural lighting, clear face with natural makeup, lifestyle photography", 'realistic', 'fashion'),
]

for filename, prompt, style, category in fashion_prompts:
    print(f'[{filename}] Generating...', end=' ')
    r = requests.post(f'{BASE}/generate', json={
        'prompt': prompt,
        'negative_prompt': 'ugly face, deformed face, blurry face, bad anatomy, bad hands, extra fingers, cropped, low quality, blurry',
        'style': style,
        'category': category,
        'num_images': 1,
        'quality': 'ultra',
        'resolution': '4k',
        'aspect_ratio': '3:4'
    }, headers=headers, timeout=120)
    if r.ok:
        images = r.json().get('images', [])
        if images:
            url = images[0]['url']
            print(f'URL: {url[:80]}...')
            print(f'  Dimensions: {images[0].get("width")}x{images[0].get("height")}')
            try:
                img_data = requests.get(url, timeout=120).content
                path = os.path.join(OUTPUT, f'{filename}.png')
                with open(path, 'wb') as f:
                    f.write(img_data)
                print(f'  Saved ({len(img_data)//1024} KB)')
            except Exception as e:
                print(f'  Download failed: {e}')
                path = os.path.join(OUTPUT, f'{filename}_url.txt')
                with open(path, 'w') as f:
                    f.write(url)
                print(f'  URL saved to text file')
        else:
            print('No images')
    else:
        print(f'FAIL: {r.json()}')
    time.sleep(1)

print(f'\nDone! Files in {OUTPUT}')
