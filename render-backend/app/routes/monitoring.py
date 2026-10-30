import asyncio
from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel

from typing import List, Optional

from app.auth import get_current_user

from app.supabase import get_supabase

from app.services.resource_monitor import ResourceMonitor

from app.services.ai.groq_provider import GroqProvider

from app.config import settings



router = APIRouter()



class ReplaceResourceRequest(BaseModel):

    new_url: str

    new_title: Optional[str] = None



@router.post("/api/tasks/{task_id}/toggle-monitor")
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

@router.get("/api/tasks/{task_id}/resources/status")
def get_resource_status(task_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        task_resp = supabase.table('tasks').select('auto_monitor_enabled').eq('id', task_id).eq('user_id', user.id).execute()
        auto_monitor = task_resp.data[0].get('auto_monitor_enabled', False) if task_resp.data else False
        
        response = supabase.table('task_resources').select('*').eq('task_id', task_id).eq('user_id', user.id).execute()
        return {"resources": response.data, "auto_monitor_enabled": auto_monitor}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/tasks/{task_id}/resources/{resource_id}/checks")

def get_resource_checks(task_id: str, resource_id: str, user=Depends(get_current_user)):

    try:

        supabase = get_supabase()

        response = supabase.table('resource_checks').select('*').eq('resource_id', resource_id).eq('task_id', task_id).eq('user_id', user.id).order('checked_at', desc=True).execute()

        return {"checks": response.data}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.post("/api/monitoring/check-all")
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

@router.post("/api/tasks/{task_id}/resources/{resource_id}/check")

async def check_resource(task_id: str, resource_id: str, user=Depends(get_current_user)):

    try:

        supabase = get_supabase()

        response = supabase.table('task_resources').select('*').eq('id', resource_id).eq('task_id', task_id).eq('user_id', user.id).execute()

        if not response.data:

            raise HTTPException(status_code=404, detail="Resource not found")

        resource = response.data[0]

        

        monitor = ResourceMonitor(supabase)

        result = await monitor.check_resource(

            resource_id=resource_id,

            url=resource['url'],

            previous_hash=resource.get('content_hash'),

            user_id=user.id,

            task_id=task_id

        )

        return {"status": "success", "result": result}

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.post("/api/tasks/{task_id}/resources/{resource_id}/toggle-ignore")
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

@router.post("/api/tasks/{task_id}/resources/{resource_id}/dismiss-alert")
def dismiss_alert(task_id: str, resource_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        supabase.table('task_resources').update({'check_status': 'available', 'is_ignored': True}).eq('id', resource_id).eq('user_id', user.id).execute()
        return {"status": "success"}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.post("/api/tasks/{task_id}/resources/{resource_id}/replacement-analysis")

async def analyze_replacement(task_id: str, resource_id: str, user=Depends(get_current_user)):

    try:

        supabase = get_supabase()

        res_resp = supabase.table('task_resources').select('*').eq('id', resource_id).eq('task_id', task_id).eq('user_id', user.id).execute()

        if not res_resp.data:

            raise HTTPException(status_code=404, detail="Resource not found")

        original_resource = res_resp.data[0]

        

        all_res_resp = supabase.table('task_resources').select('*').eq('task_id', task_id).eq('user_id', user.id).execute()

        existing_resources = all_res_resp.data



        act_resp = supabase.table('task_activity').select('*').eq('task_id', task_id).eq('user_id', user.id).order('timestamp', desc=True).limit(50).execute()

        existing_activity = act_resp.data

        

        task_resp = supabase.table('tasks').select('*').eq('id', task_id).eq('user_id', user.id).execute()

        task_name = task_resp.data[0]['name'] if task_resp.data else "Unknown Task"

        

        provider = GroqProvider(api_key=settings.GROQ_API_KEY)

        result = await provider.analyze_replacement(

            original_resource=original_resource,

            task_name=task_name,

            existing_resources=existing_resources,

            task_graph=None,

            existing_activity=existing_activity

        )

        return {"status": "success", "analysis": result.model_dump()}

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.post("/api/tasks/{task_id}/resources/{resource_id}/replace")

def replace_resource(task_id: str, resource_id: str, request: ReplaceResourceRequest, user=Depends(get_current_user)):

    try:

        supabase = get_supabase()

        from datetime import datetime

        

        new_res_data = {

            'task_id': task_id,

            'user_id': user.id,

            'url': request.new_url,

            'title': request.new_title

        }

        new_res_resp = supabase.table('task_resources').insert(new_res_data).execute()

        if not new_res_resp.data:

            raise HTTPException(status_code=500, detail="Failed to create new resource")

        new_resource = new_res_resp.data[0]

        

        update_data = {

            'replaced_at': datetime.utcnow().isoformat(),

            'replaced_by_resource_id': new_resource['id']

        }

        supabase.table('task_resources').update(update_data).eq('id', resource_id).eq('user_id', user.id).execute()

        

        return {"status": "success", "new_resource": new_resource}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

