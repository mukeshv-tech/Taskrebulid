import codecs

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

backfill_code = """
@router.get("/api/search/backfill")
async def backfill_search_documents():
    try:
        supabase = get_supabase()
        tasks = supabase.table("tasks").select("*").execute()
        resources = supabase.table("task_resources").select("*").execute()
        
        count = 0
        errors = []
        
        # Index tasks
        if tasks.data:
            for task in tasks.data:
                try:
                    success = search_indexer.index_document(
                        user_id=task.get("user_id"),
                        task_id=task.get("id"),
                        source_type="task",
                        source_id=task.get("id"),
                        title=task.get("name") or "Untitled",
                        content=task.get("description", "") or ""
                    )
                    if success:
                        count += 1
                    else:
                        errors.append(f"Task {task.get('id')} failed (returned False)")
                except Exception as ex:
                    errors.append(f"Task {task.get('id')} exception: {str(ex)}")
                    
        # Index resources
        if resources.data:
            for res in resources.data:
                try:
                    success = search_indexer.index_document(
                        user_id=res.get("user_id") or tasks.data[0].get("user_id") if tasks.data else None,
                        task_id=res.get("task_id"),
                        source_type="resource",
                        source_id=res.get("id"),
                        title=res.get("title") or res.get("url") or "Untitled",
                        content=res.get("snippet", "") or ""
                    )
                    if success:
                        count += 1
                    else:
                        errors.append(f"Resource {res.get('id')} failed (returned False)")
                except Exception as ex:
                    errors.append(f"Resource {res.get('id')} exception: {str(ex)}")
                    
        return {"status": "success", "indexed_count": count, "tasks_found": len(tasks.data) if tasks.data else 0, "resources_found": len(resources.data) if resources.data else 0, "errors": errors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

import re
code = re.sub(r'@router\.get\("/api/search/backfill"\).*?return \{"status": "success".*?\}\n    except Exception as e:\n        raise HTTPException\(status_code=500, detail=str\(e\)\)', backfill_code.strip(), code, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines(path)
