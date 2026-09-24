import codecs

path = 'render-backend/requirements.txt'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'google-generativeai>=0.4.0',
    'google-generativeai>=0.8.6'
)
code = code.replace(
    'google-generativeai\n',
    ''
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

path2 = 'render-backend/app/services/search_indexer.py'
code2 = codecs.open(path2, 'r', 'utf-8').read()

code2 = code2.replace(
    'self.model_name = "models/embedding-001"',
    'self.model_name = "models/text-embedding-004"'
)
code2 = code2.replace(
    'content=text,',
    'content=text,\n                output_dimensionality=768,'
)

with open(path2, 'w', encoding='utf-8') as f:
    f.write(code2)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines(path)
fix_newlines(path2)
