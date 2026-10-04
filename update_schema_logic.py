import codecs
import re

path = 'supabase_schema.sql'
code = codecs.open(path, 'r', 'utf-8').read()

old_logic = "AND\n        (query_text IS NULL OR d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%')"
new_logic = "AND\n        (\n            (1 - (d.embedding <=> query_embedding) > match_threshold)\n            OR\n            (query_text IS NOT NULL AND (d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%'))\n        )"

# Replace the AND (1 - embedding > threshold) AND (...)
code = code.replace("AND\n        (1 - (d.embedding <=> query_embedding) > match_threshold) AND\n        (query_text IS NULL OR d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%')", new_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
