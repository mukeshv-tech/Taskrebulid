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

if not url or not key:
    print("Missing credentials")
    exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

# Check count of documents
resp = requests.get(f"{url}/rest/v1/search_documents?select=id", headers=headers)
if resp.status_code == 200:
    docs = resp.json()
    print(f"Total search documents: {len(docs)}")
else:
    print(f"Error fetching documents: {resp.text}")

# Check if embedding is all zeros
resp = requests.get(f"{url}/rest/v1/search_documents?select=title,embedding&limit=1", headers=headers)
if resp.status_code == 200:
    docs = resp.json()
    if docs:
        emb = docs[0].get("embedding")
        if type(emb) == str:
            import json
            emb = json.loads(emb)
        print(f"Document 1 Title: {docs[0].get('title')}")
        
        if all(x == 0 for x in emb):
            print("WARNING: THE EMBEDDING IS ALL ZEROS! GEMINI IS FAILING!")
        else:
            print(f"Embedding looks normal (first 3 values): {emb[:3]}")
            print(f"Embedding dimensions: {len(emb)}")
    else:
        print("No documents found in table.")
else:
    print(f"Error: {resp.text}")
