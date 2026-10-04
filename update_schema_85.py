import codecs
import re

path = 'supabase_schema.sql'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    '(1 - (d.embedding <=> query_embedding) > 0.40)',
    '(1 - (d.embedding <=> query_embedding) > 0.85)'
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
