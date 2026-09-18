from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.auth import get_current_user
from app.supabase import get_supabase

router = APIRouter()

class TaskCreate(BaseModel):
    name: str

@router.get("/api/tasks")
def list_tasks(user = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("tasks").select("*").eq("user_id", user.id).execute()
    return result.data

@router.post("/api/tasks")
def create_task(task: TaskCreate, user = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("tasks").insert({"user_id": user.id, "name": task.name}).execute()
    if len(result.data) > 0:
        return result.data[0]
    raise HTTPException(status_code=500, detail="Failed to create task")

@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    # Check ownership
    task = supabase.table("tasks").select("user_id").eq("id", task_id).execute()
    if not task.data or task.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    supabase.table("tasks").delete().eq("id", task_id).execute()
    return {"status": "deleted"}
