import codecs

path = 'render-backend/app/services/search_indexer.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'self.model_name = "models/embedding-001"',
    'self.model_name = "models/gemini-embedding-001"'
)

# Just in case they didn't include the 'models/' prefix:
# We'll set it exactly as they want, but usually it needs the models/ prefix for python SDK.
# Let's set it to "models/gemini-embedding-001".

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines(path)
