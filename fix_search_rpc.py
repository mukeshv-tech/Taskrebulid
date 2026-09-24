import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    '''"query_text": query,
                "match_count": match_count,
                "match_threshold": match_threshold''',
    '''"query_text": query,
                "match_count": match_count,
                "match_threshold": match_threshold,
                "p_user_id": user["id"]'''
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
