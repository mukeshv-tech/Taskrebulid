import codecs
import re

path = 'render-backend/app/services/search_indexer.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'from app.config import GEMINI_API_KEY',
    'from app.config import settings'
)
code = code.replace(
    'if GEMINI_API_KEY:',
    'if settings.GEMINI_API_KEY:'
)
code = code.replace(
    'api_key=GEMINI_API_KEY',
    'api_key=settings.GEMINI_API_KEY'
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
