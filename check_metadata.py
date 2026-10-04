import os
import requests
import json

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

res = requests.get(f"{url}/rest/v1/search_documents?select=metadata&limit=5", headers=headers)
print("Metadata fetch:", res.status_code, json.dumps(res.json(), indent=2))
