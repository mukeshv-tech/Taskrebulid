from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.auth import get_current_user
from app.supabase import get_supabase
from app.services.search_indexer import search_indexer

router = APIRouter()

class TaskCreate(BaseModel):
    name: str

@router.get("/api/tasks")
def list_tasks(user = Depends(get_current_user)):
    try:
        supabase = get_supabase()
        result = supabase.table("tasks").select("*").eq("user_id", user.id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get tasks failed: {str(e)}")

@router.post("/api/tasks")
def create_task(task: TaskCreate, background_tasks: BackgroundTasks, user = Depends(get_current_user)):
    try:
        supabase = get_supabase()
        result = supabase.table("tasks").insert({"user_id": user.id, "name": task.name}).execute()
        if len(result.data) > 0:
            created_task = result.data[0]
            # Trigger background indexing
            background_tasks.add_task(
                search_indexer.index_document,
                user_id=user.id,
                task_id=created_task["id"],
                source_type="task",
                source_id=created_task["id"],
                title=created_task["name"],
                content="",
                metadata={}
            )
            return created_task
        raise HTTPException(status_code=500, detail="Failed to create task: no data returned")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create task failed: {str(e)}")

@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    # Check ownership
    task = supabase.table("tasks").select("user_id").eq("id", task_id).execute()
    if not task.data or task.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    supabase.table("tasks").delete().eq("id", task_id).execute()
    return {"status": "deleted"}
