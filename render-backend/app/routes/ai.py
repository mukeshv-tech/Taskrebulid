from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.auth import get_current_user
from app.supabase import get_supabase
from app.config import settings
from app.services.ai.service import ai_service
from app.services.ai.schemas import AIAnalysisInput, TaskResourceInput, TaskActivityInput

router = APIRouter()

@router.post("/api/tasks/{task_id}/ai/analyze")
async def analyze_task(task_id: str, provider: str = None, user = Depends(get_current_user)):
    supabase = get_supabase()
    
    # Verify ownership
    task_res = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_res.data or task_res.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")
    
    task_name = task_res.data[0]["name"]

    # Load resources
    res_res = supabase.table("task_resources").select("*").eq("task_id", task_id).limit(settings.AI_RESOURCE_LIMIT).execute()
    resources = [TaskResourceInput(id=r["id"], url=r["url"], title=r.get("title")) for r in res_res.data]

    # Load recent activity
    act_res = supabase.table("task_activity").select("*").eq("task_id", task_id).order("timestamp", desc=True).limit(settings.AI_ACTIVITY_LIMIT).execute()
    activity = [TaskActivityInput(id=a["id"], event_type=a["event_type"], url=a.get("url"), title=a.get("title"), timestamp=a["timestamp"]) for a in act_res.data]
    
    # Input
    input_data = AIAnalysisInput(
        task_id=task_id,
        task_name=task_name,
        resources=resources,
        activity=activity
    )
    
    # Run analysis
    result = await ai_service.analyze_task(input_data, provider_choice=provider)
    
    # Store result
    analysis_data = {
        "task_id": task_id,
        "user_id": user.id,
        "analysis_type": "full_task_analysis",
        "model_name": settings.MODEL_NAME,
        "model_version": "1.0",
        "input_activity_count": len(activity),
        "input_resource_count": len(resources),
        "result": result.model_dump()
    }
    
    insert_res = supabase.table("task_ai_analyses").insert(analysis_data).execute()
    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Failed to save AI analysis")
        
    return insert_res.data[0]

@router.get("/api/tasks/{task_id}/ai/analyses")
def list_analyses(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    # verify ownership
    task_res = supabase.table("tasks").select("user_id").eq("id", task_id).execute()
    if not task_res.data or task_res.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")

    res = supabase.table("task_ai_analyses").select("*").eq("task_id", task_id).order("created_at", desc=True).execute()
    return res.data
