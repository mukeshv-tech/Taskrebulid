import codecs
import re

path = 'render-backend/app/main.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_app_init = """
description = \"\"\"
# Welcome to the TaskRebuild API 🚀

TaskRebuild is an intelligent, context-aware productivity backend that automatically tracks your browsing activity, captures resources, and maps your workflow into an advanced vector-searchable Knowledge Graph.

## Core Engines
* **Google-Clone RRF Search**: A 3072-dimension semantic search engine powered by Gemini AI, merged with PostgreSQL Trigrams and Full-Text Reciprocal Rank Fusion.
* **Knowledge Graph**: Every task, resource, and browser session is mapped into a dynamic graph to help you understand how your workflows connect.
* **Live System Metrics**: Asynchronous, zero-latency monitoring of RAM, Python runtime, and vector counts.

### Getting Started
Use the interactive client on the right to instantly test any endpoint. All requests require your Supabase Auth JWT token in the `Authorization: Bearer` header.
\"\"\"

app = FastAPI(
    title="TaskRebuild API", 
    version="2.0.0",
    description=description,
    lifespan=lifespan, 
    docs_url=None, 
    redoc_url=None
)
"""

code = code.replace('app = FastAPI(title="TaskRebuild API", lifespan=lifespan, docs_url=None, redoc_url=None)', new_app_init)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
