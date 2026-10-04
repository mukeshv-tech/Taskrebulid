import os
import requests

url = ""
key = ""

with open("render-backend/.env", "r") as f:
    for line in f:
        if line.startswith("SUPABASE_URL="):
            url = line.strip().split("=")[1]
        elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
            key = line.strip().split("=")[1]

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

# 1. Fetch a user id
res = requests.get(f"{url}/rest/v1/search_documents?select=user_id&limit=1", headers=headers)
print("User ID fetch:", res.status_code, res.text)
try:
    user_id = res.json()[0]["user_id"]
except:
    user_id = "00000000-0000-0000-0000-000000000000"

# 2. Call autocomplete_search
payload = {
    "query_text": "un",
    "p_user_id": user_id,
    "match_count": 5
}
res = requests.post(f"{url}/rest/v1/rpc/autocomplete_search", headers=headers, json=payload)
print("RPC autocomplete:", res.status_code, res.text)
