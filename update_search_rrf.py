import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

# Replace hybrid_search_documents with hybrid_search_rrf
code = code.replace(
    '"hybrid_search_documents",\n            {\n                "query_embedding": query_embedding,\n                "query_text": q,\n                "match_count": match_count,\n                "match_threshold": match_threshold,\n                "p_user_id": user["id"]\n            }',
    '"hybrid_search_rrf",\n            {\n                "query_embedding": query_embedding,\n                "query_text": q,\n                "match_count": match_count,\n                "p_user_id": user["id"]\n            }'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
