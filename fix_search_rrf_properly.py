import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

# I will use a regular expression to safely replace it regardless of exact whitespace
import re
new_code = re.sub(
    r'"hybrid_search_documents",\s*\{\s*"query_embedding": query_embedding,\s*"query_text": q,\s*"match_count": match_count,\s*"match_threshold": match_threshold,\s*"p_user_id": user\.id\s*\}',
    '"hybrid_search_rrf",\n            {\n                "query_embedding": query_embedding,\n                "query_text": q,\n                "match_count": match_count,\n                "p_user_id": user.id\n            }',
    code
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
