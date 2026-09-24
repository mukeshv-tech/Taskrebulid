import codecs

path = 'render-backend/app/services/search_indexer.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'except Exception as e:\n            print(f"Error indexing document: {e}")\n            return False',
    'except Exception as e:\n            raise Exception(f"Supabase upsert failed: {e}")'
)
code = code.replace(
    'if not embedding:\n            return False',
    'if not embedding:\n            raise Exception("Gemini embedding returned empty")'
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
