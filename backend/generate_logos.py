import requests, os

BASE = 'http://localhost:5000/api'
OUTPUT = r'C:\Users\Acer\OneDrive\Documents\Default Project\arua result'

r = requests.post(f'{BASE}/login', json={'email': 'testuser2@gmail.com', 'password': 'Test1234!'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

logos = [
    ("arua-logo-01", "Minimalist tech logo for AURA AI, diamond shape with red gradient, elegant modern typography 'AURA', clean vector style, dark background, professional branding", 'minimal', 'logo'),
    ("arua-logo-02", "Luxury gold and red logo for AURA AI brand, premium emblem style, letter A monogram, elegant curves, dark background, high-end corporate branding", 'luxury', 'logo'),
    ("arua-logo-03", "Futuristic AI logo for AURA, abstract neural network design with red diamond core, glowing tech lines, dark theme, startup tech branding", 'cyberpunk', 'logo'),
    ("arua-logo-04", "Modern geometric logo for AURA AI, interconnected nodes forming letter A, red and dark gradients, clean minimal, tech startup branding", 'minimal', 'logo'),
    ("arua-logo-05", "Elegant minimalist logo mark for AURA, simple red diamond icon with smooth sans-serif text below, black background, professional brand identity", 'minimal', 'logo'),
]

for filename, prompt, style, category in logos:
    print(f'[{filename}] Generating...', end=' ')
    r = requests.post(f'{BASE}/generate', json={
        'prompt': prompt,
        'negative_prompt': 'text, watermark, signature, ugly, blurry, low quality, messy, crowded',
        'style': style, 'category': category,
        'num_images': 1, 'quality': 'ultra', 'resolution': '4k', 'aspect_ratio': '1:1'
    }, headers=headers, timeout=120)
    if r.ok:
        images = r.json().get('images', [])
        if images:
            url = images[0]['url']
            print(f'\n  URL: {url[:100]}...')
            try:
                img_data = requests.get(url, timeout=180, headers={'User-Agent': 'Mozilla/5.0'}).content
                if len(img_data) > 10000:
                    path = os.path.join(OUTPUT, f'{filename}.png')
                    with open(path, 'wb') as f:
                        f.write(img_data)
                    print(f'  Saved: {len(img_data)//1024} KB')
                else:
                    path = os.path.join(OUTPUT, f'{filename}.txt')
                    with open(path, 'w') as f:
                        f.write(url)
                    print(f'  URL saved (response too small)')
            except Exception as e:
                path = os.path.join(OUTPUT, f'{filename}.txt')
                with open(path, 'w') as f:
                    f.write(url)
                print(f'  URL saved (download error: {e})')
        else:
            print('No images')
    else:
        print(f'FAIL: {r.json()}')
    import time; time.sleep(1)

print(f'\nDone! Check {OUTPUT}')
