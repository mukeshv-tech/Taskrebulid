import codecs

path = 'render-backend/app/services/ai/gemini_provider.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'raise NotImplementedError(\\"Gemini does not support analyze_replacement yet\\")',
    'raise NotImplementedError("Gemini does not support analyze_replacement yet")'
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
