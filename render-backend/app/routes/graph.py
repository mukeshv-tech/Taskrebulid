from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.services.graph_service import get_task_graph, delete_node, delete_edge, reject_edge

router = APIRouter()

@router.get("/api/tasks/{task_id}/graph")
def get_graph(task_id: str, user = Depends(get_current_user)):
    try:
        return get_task_graph(task_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch graph: {str(e)}")

@router.delete("/api/tasks/{task_id}/graph/nodes/{node_id}")
def remove_node(task_id: str, node_id: str, user = Depends(get_current_user)):
    try:
        delete_node(task_id, node_id, user.id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete node: {str(e)}")

@router.delete("/api/tasks/{task_id}/graph/edges/{edge_id}")
def remove_edge(task_id: str, edge_id: str, user = Depends(get_current_user)):
    try:
        delete_edge(task_id, edge_id, user.id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete edge: {str(e)}")

@router.post("/api/tasks/{task_id}/graph/edges/{edge_id}/reject")
def reject_graph_edge(task_id: str, edge_id: str, user = Depends(get_current_user)):
    try:
        reject_edge(task_id, edge_id, user.id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject edge: {str(e)}")

@router.post("/api/tasks/{task_id}/graph/analyze")
async def analyze_task_graph(task_id: str, user = Depends(get_current_user)):
    from app.supabase import get_supabase
    from app.services.ai.schemas import AIAnalysisInput, TaskResourceInput, TaskActivityInput
    from app.services.ai.service import ai_service
    from app.services.graph_service import save_ai_graph
    from app.config import settings
    
    supabase = get_supabase()
    
    # Verify ownership
    task_res = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_res.data or task_res.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")
        
    task_name = task_res.data[0]["name"]
    
    # Load bounded subset for AI
    res_res = supabase.table("task_resources").select("*").eq("task_id", task_id).limit(10).execute()
    resources = [TaskResourceInput(id=r["id"], url=r["url"], title=r.get("title")) for r in res_res.data]

    act_res = supabase.table("task_activity").select("*").eq("task_id", task_id).order("timestamp", desc=True).limit(20).execute()
    activity = [TaskActivityInput(id=a["id"], event_type=a["event_type"], url=a.get("url"), title=a.get("title"), timestamp=a["timestamp"]) for a in act_res.data]
    
    input_data = AIAnalysisInput(
        task_id=task_id,
        task_name=task_name,
        resources=resources,
        activity=activity
    )
    
    result = await ai_service.analyze_graph(input_data)
    
    # Save to graph
    save_ai_graph(task_id, user.id, [n.model_dump() for n in result.nodes], [e.model_dump() for e in result.edges])
    
    return {"status": "success"}
