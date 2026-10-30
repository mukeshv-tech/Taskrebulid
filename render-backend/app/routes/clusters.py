from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.auth import get_current_user
from app.services.cluster_service import generate_clusters_for_task, get_task_clusters
from pydantic import BaseModel

router = APIRouter(prefix="/api/tasks/{task_id}/clusters", tags=["clusters"])

class ClusterResponse(BaseModel):
    id: str
    label: str
    summary: str
    rationale: str
    members: List[Dict[str, Any]]

@router.post("/generate", response_model=Dict[str, Any])
@router.post("", response_model=Dict[str, Any])
async def trigger_cluster_generation(task_id: str, user = Depends(get_current_user)):
    """
    Triggers dynamic re-clustering of a task's sub-tasks based on current knowledge graph relationships.
    Returns the generated clusters directly so the frontend can update immediately.
    """
    user_id = user.id
    try:
        clusters = await generate_clusters_for_task(task_id, user_id)
        return {
            "status": "success",
            "message": f"Successfully generated {len(clusters)} clusters.",
            "clusters": clusters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[Dict[str, Any]])
async def fetch_task_clusters(task_id: str, user = Depends(get_current_user)):
    """
    Returns the current clusters and their assigned sub-tasks/nodes for a specific task.
    """
    user_id = user.id
    return get_task_clusters(task_id, user_id)
