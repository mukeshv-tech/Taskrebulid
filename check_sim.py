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

# Fetch the first document's embedding to use as a query
resp = requests.get(f"{url}/rest/v1/search_documents?select=title,embedding&limit=1", headers=headers)
docs = resp.json()
query_emb = docs[0].get("embedding")

# Call the RPC with match_threshold = 0.0
payload = {
    "query_embedding": query_emb,
    "query_text": None,
    "match_count": 5,
    "match_threshold": 0.0,
    "p_user_id": "00000000-0000-0000-0000-000000000000"  # this will return nothing if user_id doesn't match
}
# wait, if I don't know the user_id, I can just do a similarity query in python to find the actual threshold!
# let me fetch two embeddings and compute their similarity in python
resp2 = requests.get(f"{url}/rest/v1/search_documents?select=title,embedding&limit=2", headers=headers)
docs2 = resp2.json()

if len(docs2) == 2:
    emb1 = json.loads(docs2[0]["embedding"]) if type(docs2[0]["embedding"])==str else docs2[0]["embedding"]
    emb2 = json.loads(docs2[1]["embedding"]) if type(docs2[1]["embedding"])==str else docs2[1]["embedding"]
    
    import math
    def cosine_similarity(v1, v2):
        dot = sum(x*y for x,y in zip(v1,v2))
        mag1 = math.sqrt(sum(x*x for x in v1))
        mag2 = math.sqrt(sum(x*x for x in v2))
        return dot / (mag1 * mag2)
        
    print(f"Similarity between '{docs2[0]['title']}' and '{docs2[1]['title']}': {cosine_similarity(emb1, emb2)}")
    print(f"Similarity with itself: {cosine_similarity(emb1, emb1)}")

