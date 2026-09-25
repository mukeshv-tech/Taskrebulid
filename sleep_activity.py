import codecs
import re

path = 'render-backend/app/routes/activity.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_post = """
from fastapi import BackgroundTasks
import time

def index_activities_bg(user_id: str, task_id: str, inserted_events: List[Dict[str, Any]]):
    from app.services.search_indexer import search_indexer
    for act in inserted_events:
        if not act.get("title") and not act.get("url"):
            continue
        try:
            search_indexer.index_document(
                user_id=user_id,
                task_id=task_id,
                source_type="activity",
                source_id=act.get("id"),
                title=act.get("title") or "Browser Activity",
                content=act.get("url") or ""
            )
        except Exception as e:
            print(f"Background activity indexing failed: {e}")
        time.sleep(0.2) # Yield CPU

@router.post("/api/tasks/{task_id}/activity")
def add_task_activity(task_id: str, batch: ActivityBatch, background_tasks: BackgroundTasks, user = Depends(get_current_user)):
    try:
        # Convert Pydantic models to dicts
        events_dict = [event.model_dump() for event in batch.events]
        result = record_activity(task_id, user.id, events_dict)
        if result:
            background_tasks.add_task(index_activities_bg, user.id, task_id, result)
        return {"status": "success", "count": len(result)}
"""

code = re.sub(
    r'from fastapi import BackgroundTasks.*?def index_activities_bg.*?return \{"status": "success", "count": len\(result\)\}',
    new_post.strip(),
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
