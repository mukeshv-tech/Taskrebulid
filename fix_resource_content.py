import codecs
import re

# Fix backfill script
path_search = 'render-backend/app/routes/search.py'
code = codecs.open(path_search, 'r', 'utf-8').read()

code = code.replace(
    'title=res.get("title") or res.get("url") or "Untitled",\n                        content=res.get("url") or ""',
    'title=res.get("title") or res.get("url") or "Untitled",\n                        content=f"{res.get(\'description\', \'\')} \\n {res.get(\'url\', \'\')}"'
)

with open(path_search, 'w', encoding='utf-8') as f:
    f.write(code)

# Fix resources.py
path_resources = 'render-backend/app/routes/resources.py'
code2 = codecs.open(path_resources, 'r', 'utf-8').read()

code2 = code2.replace(
    'content=new_resource.get("url", ""),',
    'content=f"{new_resource.get(\'description\', \'\')} \\n {new_resource.get(\'url\', \'\')}",'
)

with open(path_resources, 'w', encoding='utf-8') as f:
    f.write(code2)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines(path_search)
fix_newlines(path_resources)
