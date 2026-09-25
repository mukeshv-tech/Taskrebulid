import codecs

path = 'render-backend/app/services/ai/gemini_provider.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'result_text = response.text\n            result_json = json.loads(result_text)',
    'result_text = response.text\n            logger.error("RAW GEMINI GRAPH OUTPUT: " + result_text)\n            result_json = json.loads(result_text)'
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
