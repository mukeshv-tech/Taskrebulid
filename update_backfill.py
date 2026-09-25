import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

# First, let's update the backfill script
new_backfill = """
@router.get("/api/search/backfill")
async def backfill_search_documents():
    try:
        supabase = get_supabase()
        tasks = supabase.table("tasks").select("*").execute()
        resources = supabase.table("task_resources").select("*").execute()
        activities = supabase.table("task_activity").select("*").execute()
        
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
                    if success: count += 1
                except Exception as ex:
                    errors.append(f"Task {task.get('id')} failed: {str(ex)}")

        # Index resources
        if resources.data:
            for res in resources.data:
                try:
                    success = search_indexer.index_document(
                        user_id=res.get("user_id"),
                        task_id=res.get("task_id"),
                        source_type="resource",
                        source_id=res.get("id"),
                        title=res.get("title") or res.get("url") or "Untitled",
                        content=res.get("url") or ""
                    )
                    if success: count += 1
                except Exception as ex:
                    errors.append(f"Resource {res.get('id')} failed: {str(ex)}")

        # Index activities
        if activities.data:
            for act in activities.data:
                # Only index if it has a title or URL
                if not act.get("title") and not act.get("url"):
                    continue
                try:
                    success = search_indexer.index_document(
                        user_id=act.get("user_id"),
                        task_id=act.get("task_id"),
                        source_type="activity",
                        source_id=act.get("id"),
                        title=act.get("title") or "Browser Activity",
                        content=act.get("url") or ""
                    )
                    if success: count += 1
                except Exception as ex:
                    errors.append(f"Activity {act.get('id')} failed: {str(ex)}")
                    
        return {"status": "success", "indexed": count, "errors": errors}
    except Exception as e:
        return {"status": "error", "message": str(e)}
"""

# Replace the old backfill
code = re.sub(
    r'@router\.get\("/api/search/backfill"\).*?(?=\n\n|\Z)',
    new_backfill.strip(),
    code,
    flags=re.DOTALL
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
