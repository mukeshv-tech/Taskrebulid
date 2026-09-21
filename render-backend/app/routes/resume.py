from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.auth import get_current_user
from app.supabase import get_supabase
from app.config import settings
from app.services.ai.service import ai_service
from app.services.ai.schemas import AIResumeInput

router = APIRouter()

@router.post("/api/tasks/{task_id}/resume/analyze")
async def analyze_resume(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    
    # Verify task ownership
    task_res = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_res.data or task_res.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")
    
    task_name = task_res.data[0]["name"]

    # Gather resources
    res_res = supabase.table("task_resources").select("*").eq("task_id", task_id).limit(settings.AI_RESUME_MAX_RESOURCES).execute()
    resources = [{"id": r["id"], "url": r["url"], "title": r.get("title")} for r in res_res.data]

    # Gather activity
    act_res = supabase.table("task_activity").select("*").eq("task_id", task_id).order("timestamp", desc=True).limit(settings.AI_RESUME_MAX_ACTIVITY).execute()
    activity = [{"id": a["id"], "event_type": a["event_type"], "url": a.get("url"), "title": a.get("title"), "timestamp": a["timestamp"]} for a in act_res.data]
    
    # Latest AI analysis
    ai_res = supabase.table("task_ai_analyses").select("result").eq("task_id", task_id).order("created_at", desc=True).limit(1).execute()
    latest_analysis = ai_res.data[0]["result"] if ai_res.data else None

    # Latest task graph
    graph_nodes = supabase.table("task_nodes").select("*").eq("task_id", task_id).limit(settings.AI_RESUME_MAX_GRAPH_NODES).execute()
    graph_edges = supabase.table("task_edges").select("*").eq("task_id", task_id).limit(settings.AI_RESUME_MAX_GRAPH_EDGES).execute()
    task_graph = {"nodes": graph_nodes.data, "edges": graph_edges.data} if graph_nodes.data else None

    # Previous snapshot
    snap_res = supabase.table("task_snapshots").select("state").eq("task_id", task_id).order("created_at", desc=True).limit(1).execute()
    previous_snapshot = snap_res.data[0]["state"] if snap_res.data else None

    input_data = AIResumeInput(
        task_id=task_id,
        task_name=task_name,
        resources=resources,
        activity=activity,
        latest_analysis=latest_analysis,
        task_graph=task_graph,
        previous_snapshot=previous_snapshot
    )
    
    result = await ai_service.analyze_resume(input_data)
    
    # Create Snapshot
    state_json = {
        "active_resources": resources,
        "recent_activity": activity,
        "resume_analysis": result.model_dump()
    }
    
    snapshot_data = {
        "task_id": task_id,
        "user_id": user.id,
        "snapshot_type": "resume",
        "summary": result.resume_summary,
        "state": state_json,
        "activity_count": len(activity),
        "resource_count": len(resources),
        "graph_node_count": len(graph_nodes.data) if graph_nodes.data else 0,
        "graph_edge_count": len(graph_edges.data) if graph_edges.data else 0
    }
    
    insert_res = supabase.table("task_snapshots").insert(snapshot_data).execute()
    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Failed to save snapshot")
        
    return insert_res.data[0]

@router.get("/api/tasks/{task_id}/resume")
def get_latest_resume(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    
    # Verify task ownership
    task_res = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user.id).execute()
    if not task_res.data:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")
        
    snap_res = supabase.table("task_snapshots").select("*").eq("task_id", task_id).eq("snapshot_type", "resume").order("created_at", desc=True).limit(1).execute()
    if not snap_res.data:
        return None
    return snap_res.data[0]

@router.delete("/api/tasks/{task_id}/resume")
def delete_resume(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    
    # Verify task ownership
    task_res = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user.id).execute()
    if not task_res.data:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")
        
    res = supabase.table("task_snapshots").delete().eq("task_id", task_id).eq("snapshot_type", "resume").execute()
    return {"status": "success", "deleted": len(res.data) if res.data else 0}

@router.get("/api/tasks/{task_id}/snapshots")
def get_task_snapshots(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    task_res = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user.id).execute()
    if not task_res.data:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    snap_res = supabase.table("task_snapshots").select("*").eq("task_id", task_id).order("created_at", desc=True).limit(settings.AI_RESUME_MAX_SNAPSHOTS).execute()
    return snap_res.data

@router.get("/api/tasks/{task_id}/snapshots/{snapshot_id}")
def get_task_snapshot(task_id: str, snapshot_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    snap_res = supabase.table("task_snapshots").select("*").eq("id", snapshot_id).eq("task_id", task_id).eq("user_id", user.id).execute()
    if not snap_res.data:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snap_res.data[0]

class RestoreWorkspaceRequest(BaseModel):
    urls: List[str]

@router.post("/api/tasks/{task_id}/workspace/restore")
def restore_workspace(task_id: str, request: RestoreWorkspaceRequest, user = Depends(get_current_user)):
    supabase = get_supabase()
    task_res = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user.id).execute()
    if not task_res.data:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Gather all URLs associated with this task to validate against
    res_res = supabase.table("task_resources").select("url").eq("task_id", task_id).execute()
    act_res = supabase.table("task_activity").select("url").eq("task_id", task_id).execute()
    
    valid_urls = set()
    for r in res_res.data:
        valid_urls.add(r["url"])
    for a in act_res.data:
        if a.get("url"):
            valid_urls.add(a["url"])
            
    urls_to_restore = [url for url in request.urls if url in valid_urls]
    return {"status": "success", "urls": urls_to_restore}
