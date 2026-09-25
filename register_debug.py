import codecs
import re

path = 'render-backend/app/main.py'
code = codecs.open(path, 'r', 'utf-8').read()

if "from app.routes import debug" not in code:
    code = code.replace(
        'from app.routes import auth, tasks, resources, ai, search, monitoring, graph',
        'from app.routes import auth, tasks, resources, ai, search, monitoring, graph, debug'
    )
    code = code.replace(
        'app.include_router(graph.router)',
        'app.include_router(graph.router)\napp.include_router(debug.router)'
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
