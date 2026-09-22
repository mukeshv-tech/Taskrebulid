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

@router.get("/api/tasks/{task_id}/resources/status")
def get_resource_status(task_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        response = supabase.table('task_resources').select('*').eq('task_id', task_id).eq('user_id', user.id).execute()
        return {"resources": response.data}
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
