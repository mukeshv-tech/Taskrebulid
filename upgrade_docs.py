import codecs
import re

path = 'render-backend/app/main.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_app_init = """from fastapi.responses import HTMLResponse

app = FastAPI(title="TaskRebuild API", lifespan=lifespan, docs_url=None, redoc_url=None)

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    html = f\"\"\"
    <!DOCTYPE html>
    <html>
    <head>
        <title>TaskRebuild API - Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <!-- Inject Scalar API Reference -->
        <script 
            id="api-reference" 
            data-url="{app.openapi_url}" 
            data-theme="moon"
            data-layout="modern"
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
    </body>
    </html>
    \"\"\"
    return HTMLResponse(html)
"""

code = code.replace('app = FastAPI(title="TaskRebuild Backend", lifespan=lifespan)', new_app_init)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
