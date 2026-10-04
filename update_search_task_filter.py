import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

# 1. Update the RPC call to pass p_task_ids
old_rpc = """        response = get_supabase().rpc(
            "hybrid_search_rrf",
            {
                "query_embedding": query_embedding,
                "query_text": q,
                "match_count": match_count,
                "p_user_id": user.id
            }
        ).execute()"""

new_rpc = """        response = get_supabase().rpc(
            "hybrid_search_rrf",
            {
                "query_embedding": query_embedding,
                "query_text": q,
                "match_count": match_count,
                "p_user_id": user.id,
                "p_task_ids": [task_id] if task_id else None
            }
        ).execute()"""

code = code.replace(old_rpc, new_rpc)

# 2. Remove the inefficient python-side filtering since the DB handles it now!
old_filtering = """        results = response.data
        if task_id:
            results = [r for r in results if r.get("task_id") == task_id]"""

new_filtering = """        results = response.data"""

code = code.replace(old_filtering, new_filtering)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
