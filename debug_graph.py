import codecs
import re

path = 'render-backend/app/routes/graph.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_block = """
    act_res = supabase.table("task_activity").select("*").eq("task_id", task_id).order("timestamp", desc=True).limit(settings.AI_ACTIVITY_LIMIT).execute()
    activity = [TaskActivityInput(id=a["id"], event_type=a["event_type"], url=a.get("url"), title=a.get("title"), timestamp=a["timestamp"]) for a in act_res.data]
    
    print(f"DEBUG: Found {len(resources)} resources and {len(activity)} activities for task {task_id}")
"""

code = code.replace(
    'act_res = supabase.table("task_activity").select("*").eq("task_id", task_id).order("timestamp", desc=True).limit(settings.AI_ACTIVITY_LIMIT).execute()\n    activity = [TaskActivityInput(id=a["id"], event_type=a["event_type"], url=a.get("url"), title=a.get("title"), timestamp=a["timestamp"]) for a in act_res.data]',
    new_block.strip()
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
