import requests, os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
UID = "9d10a39a-3fb5-4334-9686-47b4e77dd53e"
BASE = "http://localhost:5000/api"

# Step 1: Set credits to 30 and reset last_credit_refill to 25 hours ago
print("Setting up test state...")
r = requests.patch(
    f'{SUPABASE_URL}/rest/v1/profiles?user_id=eq.{UID}',
    headers={
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    },
    json={'ai_credits': 30, 'last_credit_refill': '2026-07-24T06:00:00+00:00'}
)
print("Update:", r.status_code, r.json())

# Step 2: Login to trigger refill
print("\nLogging in...")
r = requests.post(f"{BASE}/login", json={"email": "testuser2@gmail.com", "password": "Test1234!"})
print("Login:", r.status_code)
data = r.json()
print("Credits now:", data.get('user', {}).get('ai_credits'))
print("Success:", data.get('success'))

# Step 3: Verify in database
r = requests.get(
    f'{SUPABASE_URL}/rest/v1/profiles?user_id=eq.{UID}&select=ai_credits,last_credit_refill',
    headers={
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}'
    }
)
print("\nDB state:", r.json())
