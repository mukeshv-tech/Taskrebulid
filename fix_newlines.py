import os

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    # Replace \r\r\n or \r\n with just \n
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines('render-backend/app/routes/search.py')
fix_newlines('render-backend/app/services/search_indexer.py')
