import codecs

path = 'render-backend/app/routes/monitoring.py'
code = codecs.open(path, 'r', 'utf-8').read()

imports = '''from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from app.auth import get_current_user'''

code = code.replace('from fastapi import APIRouter, Depends, HTTPException\nfrom pydantic import BaseModel\nfrom typing import List, Optional\nfrom app.auth import get_current_user', imports)

# 1. toggle-monitor endpoint
toggle_monitor = '''@router.post("/api/tasks/{task_id}/toggle-monitor")
def toggle_monitor(task_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        task_resp = supabase.table('tasks').select('auto_monitor_enabled').eq('id', task_id).eq('user_id', user.id).execute()
        if not task_resp.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        current_state = task_resp.data[0].get('auto_monitor_enabled', False)
        new_state = not current_state
        
        supabase.table('tasks').update({'auto_monitor_enabled': new_state}).eq('id', task_id).eq('user_id', user.id).execute()
        return {"status": "success", "auto_monitor_enabled": new_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tasks/{task_id}/resources/status")'''

code = code.replace('@router.get("/api/tasks/{task_id}/resources/status")', toggle_monitor)

# 2. check-all endpoint
check_all = '''@router.post("/api/monitoring/check-all")
async def check_all_monitored(user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        
        # Get all tasks with auto-monitor enabled
        tasks_resp = supabase.table('tasks').select('id').eq('user_id', user.id).eq('auto_monitor_enabled', True).execute()
        if not tasks_resp.data:
            return {"status": "success", "checked": 0, "alerts": []}
            
        task_ids = [t['id'] for t in tasks_resp.data]
        
        # Get all resources for these tasks that are not ignored and not replaced
        resources_resp = supabase.table('task_resources').select('*').eq('user_id', user.id).in_('task_id', task_ids).is_('replaced_by_resource_id', 'null').execute()
        resources = [r for r in resources_resp.data if not r.get('is_ignored')]
        
        if not resources:
            return {"status": "success", "checked": 0, "alerts": []}
            
        monitor = ResourceMonitor(supabase)
        
        async def check_single(r):
            res = await monitor.check_resource(r['id'], r['url'], r.get('content_hash'), user.id, r['task_id'])
            # Return true if it needs attention
            return r if (res.get('check_status') and res.get('check_status') != 'available') else None
            
        results = await asyncio.gather(*[check_single(r) for r in resources])
        alerts = [r for r in results if r]
        
        return {"status": "success", "checked": len(resources), "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/tasks/{task_id}/resources/{resource_id}/check")'''

code = code.replace('@router.post("/api/tasks/{task_id}/resources/{resource_id}/check")', check_all)

# 3. Update get_resource_status to return auto_monitor_enabled
get_status_replacement = '''@router.get("/api/tasks/{task_id}/resources/status")
def get_resource_status(task_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        task_resp = supabase.table('tasks').select('auto_monitor_enabled').eq('id', task_id).eq('user_id', user.id).execute()
        auto_monitor = task_resp.data[0].get('auto_monitor_enabled', False) if task_resp.data else False
        
        response = supabase.table('task_resources').select('*').eq('task_id', task_id).eq('user_id', user.id).execute()
        return {"resources": response.data, "auto_monitor_enabled": auto_monitor}'''

code = code.replace('''@router.get("/api/tasks/{task_id}/resources/status")
def get_resource_status(task_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        response = supabase.table('task_resources').select('*').eq('task_id', task_id).eq('user_id', user.id).execute()
        return {"resources": response.data}''', get_status_replacement)


# 4. Update dismiss-alert to set is_ignored = True
dismiss = '''@router.post("/api/tasks/{task_id}/resources/{resource_id}/dismiss-alert")
def dismiss_alert(task_id: str, resource_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        supabase.table('task_resources').update({'check_status': 'available', 'is_ignored': True}).eq('id', resource_id).eq('user_id', user.id).execute()
        return {"status": "success"}'''

code = code.replace('''@router.post("/api/tasks/{task_id}/resources/{resource_id}/dismiss-alert")
def dismiss_alert(task_id: str, resource_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        supabase.table('task_resources').update({'check_status': 'available'}).eq('id', resource_id).eq('user_id', user.id).execute()
        return {"status": "success"}''', dismiss)


with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
