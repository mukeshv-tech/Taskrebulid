import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

old_grouping = """        # Group results by task
        grouped_results = {}
        for row in results:
            source_type = row.get("source_type", "unknown")
            if source_type not in grouped_results:
                grouped_results[source_type] = []
            grouped_results[source_type].append(row)"""

new_grouping = """        # Group results by task
        grouped_results = {}
        for row in results:
            source_type = row.get("source_type", "unknown")
            
            # Extract URL from metadata for the frontend
            meta = row.get("metadata") or {}
            row["url"] = meta.get("url")
            
            if source_type not in grouped_results:
                grouped_results[source_type] = []
            grouped_results[source_type].append(row)"""

code = code.replace(old_grouping, new_grouping)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
