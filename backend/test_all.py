import requests, json

BASE = "http://localhost:5000/api"
TOKEN = None
USER_ID = None

def section(name):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

def req(method, path, **kwargs):
    url = f"{BASE}{path}"
    headers = kwargs.pop('headers', {})
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    fn = getattr(requests, method.lower())
    try:
        r = fn(url, headers=headers, timeout=10, **kwargs)
        print(f"  {method.upper()} {path} => {r.status_code}", end="")
        data = r.json()
        if r.ok:
            print(" OK")
        else:
            print(f" FAIL {data.get('error','')} | {str(data)[:120]}")
        return data
    except Exception as e:
        print(f"  {method.upper()} {path} => EXCEPTION {e}")
        return None

# 1. Health
section("1. Health Check")
req("GET", "/health")

# 2. Signup (might fail if exists, that's ok)
section("2. Signup")
req("POST", "/signup", json={
    "email": "testuser2@gmail.com",
    "password": "Test1234!",
    "username": "testuser2"
})

# 3. Login
section("3. Login")
data = req("POST", "/login", json={
    "email": "testuser2@gmail.com",
    "password": "Test1234!"
})
if data and data.get('access_token'):
    TOKEN = data['access_token']
    USER_ID = data.get('user', {}).get('id')
    print(f"  Token: {TOKEN[:30]}...")
    print(f"  User: {data.get('user', {}).get('username')} ({data.get('user', {}).get('role')})")

# 4. Me
section("4. Get Me")
req("GET", "/me")

# 5. Dashboard
section("5. Dashboard Data")
req("GET", "/dashboard")

# 6. Profile
section("6. Profile")
req("GET", "/profile")

# 7. History
section("7. Generation History")
req("GET", "/history")

# 8. Gallery
section("8. Gallery")
req("GET", "/gallery")

# 9. Favorites
section("9. Favorites")
req("GET", "/favorites")

# 10. Collections
section("10. Collections")
req("GET", "/collections")

# 11. Generate (test with a simple prompt - will consume credits)
section("11. Image Generation")
data = req("POST", "/generate", json={
    "prompt": "a cute cat",
    "style": "realistic",
    "category": "animals",
    "num_images": 1,
    "quality": "standard",
    "aspect_ratio": "1:1"
})

# 12. Enhance Prompt
section("12. Enhance Prompt")
req("POST", "/enhance-prompt", json={"prompt": "a sunset over mountains"})

# 13. Editor - Upscale (needs an image_id)
section("13. Editor Endpoints (skip - need image_id)")

# 14. Admin stats (user is admin)
section("14. Admin Stats")
req("GET", "/admin/stats")

section("15. Admin Users")
req("GET", "/admin/users")

section("16. Admin Images")
req("GET", "/admin/images")

print(f"\n{'='*60}")
print("  ALL TESTS COMPLETE")
print(f"{'='*60}")
