import codecs

path = 'render-backend/app/routes/metrics.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    '"ONNX bge-small-en-v1.5 (Avg Chunking x10)"',
    '"Gemini Embedding 001 (Cloud)"'
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
