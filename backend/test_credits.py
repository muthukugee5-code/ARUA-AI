import requests
BASE = "http://localhost:5000/api"

# Login
r = requests.post(f"{BASE}/login", json={"email": "testuser2@gmail.com", "password": "Test1234!"})
print("Login:", r.status_code)
data = r.json()
print("Credits:", data.get("credit_balance", data.get("ai_credits", "N/A")))
print("Full response:", data)
