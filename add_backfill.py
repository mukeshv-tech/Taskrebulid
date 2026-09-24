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
        
        # Index tasks
        if tasks.data:
            for task in tasks.data:
                success = search_indexer.index_document(
                    user_id=task.get("user_id"),
                    task_id=task.get("id"),
                    source_type="task",
                    source_id=task.get("id"),
                    title=task.get("name"),
                    content=task.get("description", "") or ""
                )
                if success:
                    count += 1
                    
        # Index resources
        if resources.data:
            for res in resources.data:
                success = search_indexer.index_document(
                    user_id=res.get("user_id") or tasks.data[0].get("user_id"), # fallback if no user_id on resource
                    task_id=res.get("task_id"),
                    source_type="resource",
                    source_id=res.get("id"),
                    title=res.get("title") or res.get("url"),
                    content=res.get("snippet", "") or ""
                )
                if success:
                    count += 1
                    
        return {"status": "success", "indexed_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

code = code.replace('@router.get("/api/search/suggestions")', backfill_code + '\n@router.get("/api/search/suggestions")')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines(path)
