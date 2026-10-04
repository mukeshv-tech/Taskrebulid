import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

old_resource = """                    search_indexer.index_document(
                        user_id=res.get("user_id"),
                        task_id=res.get("task_id"),
                        source_type="resource",
                        source_id=res.get("id"),
                        title=res.get("title") or res.get("url") or "Untitled",
                        content=f"{res.get('description', '')} \\n {res.get('url', '')}"
                    )"""

new_resource = """                    search_indexer.index_document(
                        user_id=res.get("user_id"),
                        task_id=res.get("task_id"),
                        source_type="resource",
                        source_id=res.get("id"),
                        title=res.get("title") or res.get("url") or "Untitled",
                        content=f"{res.get('description', '')} \\n {res.get('url', '')}",
                        metadata={"url": res.get("url")}
                    )"""

code = code.replace(old_resource, new_resource)

old_activity = """                    search_indexer.index_document(
                        user_id=act.get("user_id"),
                        task_id=act.get("task_id"),
                        source_type="activity",
                        source_id=act.get("id"),
                        title=act.get("title") or "Browser Activity",
                        content=act.get("url") or ""
                    )"""

new_activity = """                    search_indexer.index_document(
                        user_id=act.get("user_id"),
                        task_id=act.get("task_id"),
                        source_type="activity",
                        source_id=act.get("id"),
                        title=act.get("title") or "Browser Activity",
                        content=act.get("url") or "",
                        metadata={"url": act.get("url")}
                    )"""

code = code.replace(old_activity, new_activity)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
