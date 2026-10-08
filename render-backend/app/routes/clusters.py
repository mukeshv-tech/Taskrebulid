from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from app.auth import get_current_user
from app.services.cluster_service import generate_clusters_for_task, get_task_clusters
from pydantic import BaseModel

router = APIRouter(prefix="/tasks/{task_id}/clusters", tags=["clusters"])

class ClusterResponse(BaseModel):
    id: str
    label: str
    summary: str
    rationale: str
    members: List[Dict[str, Any]]

@router.post("/generate", response_model=Dict[str, str])
async def trigger_cluster_generation(task_id: str, background_tasks: BackgroundTasks, user = Depends(get_current_user)):
    """
    Triggers dynamic re-clustering of a task's sub-tasks based on current knowledge graph relationships.
    Runs asynchronously since LLM graph analysis can take a few seconds.
    """
    user_id = user.id
    
    # Run the generation in the background
    background_tasks.add_task(generate_clusters_for_task, task_id, user_id)
    
    return {"status": "clustering_started", "message": "Clustering process initiated in the background."}

@router.get("", response_model=List[Dict[str, Any]])
async def fetch_task_clusters(task_id: str, user = Depends(get_current_user)):
    """
    Returns the current clusters and their assigned sub-tasks/nodes for a specific task.
    """
    user_id = user.id
    return get_task_clusters(task_id, user_id)
