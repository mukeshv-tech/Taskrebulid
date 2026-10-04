import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

# Fix grouping by source_type instead of task_id
code = code.replace(
    'task_id = row["task_id"]',
    'source_type = row.get("source_type", "unknown")'
).replace(
    'if task_id not in grouped_results:',
    'if source_type not in grouped_results:'
).replace(
    'grouped_results[task_id] = []',
    'grouped_results[source_type] = []'
).replace(
    'grouped_results[task_id].append(row)',
    'grouped_results[source_type].append(row)'
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
