import re

path = 'render-backend/app/routes/monitoring.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

new_endpoint = """@router.post("/api/tasks/{task_id}/resources/{resource_id}/toggle-ignore")
def toggle_ignore(task_id: str, resource_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        res = supabase.table('task_resources').select('is_ignored').eq('id', resource_id).eq('user_id', user.id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        current = res.data[0].get('is_ignored', False)
        supabase.table('task_resources').update({'is_ignored': not current}).eq('id', resource_id).eq('user_id', user.id).execute()
        return {"status": "success", "is_ignored": not current}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""

code = code.replace('@router.post("/api/tasks/{task_id}/resources/{resource_id}/dismiss-alert")', new_endpoint + '@router.post("/api/tasks/{task_id}/resources/{resource_id}/dismiss-alert")')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
