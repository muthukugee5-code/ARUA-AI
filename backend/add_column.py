import requests, os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

sql = "ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS last_credit_refill TIMESTAMPTZ;"

r = requests.post(
    f'{SUPABASE_URL}/rest/v1/rpc/',
    headers={
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    json={}
)

print(f"Supabase REST doesn't support raw SQL. Please run this in Supabase SQL Editor:")
print(sql)
