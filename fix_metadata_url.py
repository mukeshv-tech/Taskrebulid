import os
import requests
import json
import re

url_env = ""
key_env = ""

with open("render-backend/.env", "r") as f:
    for line in f:
        if line.startswith("SUPABASE_URL="):
            url_env = line.strip().split("=")[1]
        elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
            key_env = line.strip().split("=")[1]

headers = {
    "apikey": key_env,
    "Authorization": f"Bearer {key_env}",
    "Content-Type": "application/json"
}

url_pattern = re.compile(r'(https?://[^\s]+)')

# Fetch all documents
res = requests.get(f"{url_env}/rest/v1/search_documents?select=id,content,metadata", headers=headers)
docs = res.json()

updated = 0
for doc in docs:
    meta = doc.get("metadata", {})
    if "url" not in meta and doc.get("content"):
        match = url_pattern.search(doc["content"])
        if match:
            meta["url"] = match.group(1)
            # Update the document
            update_res = requests.patch(f"{url_env}/rest/v1/search_documents?id=eq.{doc['id']}", headers=headers, json={"metadata": meta})
            if update_res.status_code < 300:
                updated += 1

print(f"Updated {updated} documents with URL in metadata.")
