import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'query_embedding, _ = search_indexer.onnx_provider.generate_embedding(q)',
    'query_embedding, _ = search_indexer.provider.generate_embedding(q)'
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
