import codecs

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_search = """
@router.get("/api/search")
def search(
    q: str, 
    model: str = "gemini", 
    user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        
        # Determine which model to use
        if model == "onnx":
            query_embedding = search_indexer.onnx_provider.generate_embedding(q)
            rpc_func = "hybrid_search_documents_onnx"
        else:
            query_embedding = search_indexer.gemini_provider.generate_embedding(q)
            rpc_func = "hybrid_search_documents_gemini"

        result = supabase.rpc(
            rpc_func,
            {
                "query_embedding": query_embedding,
                "query_text": q,
                "match_count": 20,
                "match_threshold": 0.75,
                "p_user_id": user.id
            }
        ).execute()
"""

import re
code = re.sub(r'@router\.get\("/api/search"\)\ndef search\(.*?execute\(\)', new_search.strip(), code, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
