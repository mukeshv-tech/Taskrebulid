import codecs
import re

# Update main.py
path = 'render-backend/app/main.py'
code = codecs.open(path, 'r', 'utf-8').read()

if "from app.routes import metrics" not in code:
    code = code.replace(
        'from app.routes import health, auth, tasks, resources, activity, ai, graph, resume, monitoring, search, debug',
        'from app.routes import health, auth, tasks, resources, activity, ai, graph, resume, monitoring, search, debug, metrics'
    )
    code = code.replace(
        'app.include_router(debug.router)',
        'app.include_router(debug.router)\napp.include_router(metrics.router)'
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

# Update requirements
req_path = 'render-backend/requirements.txt'
reqs = codecs.open(req_path, 'r', 'utf-8').read()
if "psutil" not in reqs:
    reqs += "\npsutil>=5.9.0\n"
    with open(req_path, 'w', encoding='utf-8') as f:
        f.write(reqs)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
fix_newlines(req_path)
