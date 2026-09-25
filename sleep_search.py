import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_backfill = """
from fastapi import BackgroundTasks
import time

def run_backfill_bg():
    try:
        supabase = get_supabase()
        tasks = supabase.table("tasks").select("*").execute()
        resources = supabase.table("task_resources").select("*").execute()
        
        # Paginate activities if huge
        activities = supabase.table("task_activity").select("*").execute()
        
        count = 0
        
        # Index tasks
        if tasks.data:
            for task in tasks.data:
                try:
                    search_indexer.index_document(
                        user_id=task.get("user_id"),
                        task_id=task.get("id"),
                        source_type="task",
                        source_id=task.get("id"),
                        title=task.get("name") or "Untitled",
                        content=task.get("description", "") or ""
                    )
                except: pass
                time.sleep(0.2) # Yield CPU to prevent freezing server

        # Index resources
        if resources.data:
            for res in resources.data:
                try:
                    search_indexer.index_document(
                        user_id=res.get("user_id"),
                        task_id=res.get("task_id"),
                        source_type="resource",
                        source_id=res.get("id"),
                        title=res.get("title") or res.get("url") or "Untitled",
                        content=res.get("url") or ""
                    )
                except: pass
                time.sleep(0.2)

        # Index activities
        if activities.data:
            for act in activities.data:
                if not act.get("title") and not act.get("url"):
                    continue
                try:
                    search_indexer.index_document(
                        user_id=act.get("user_id"),
                        task_id=act.get("task_id"),
                        source_type="activity",
                        source_id=act.get("id"),
                        title=act.get("title") or "Browser Activity",
                        content=act.get("url") or ""
                    )
                except: pass
                time.sleep(0.2)
    except Exception as e:
        print(f"Backfill failed: {e}")

@router.get("/api/search/backfill")
async def backfill_search_documents(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_backfill_bg)
    return {"status": "success", "message": "Backfill has been started in the background. Check your /api/metrics dashboard in a few minutes to see the Vectors count increase!"}
"""

code = re.sub(
    r'from fastapi import BackgroundTasks.*?def run_backfill_bg\(\):.*?return \{"status": "success", "message": "Backfill has been started in the background[^}]*\}',
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
