from app.supabase import get_supabase
from typing import List, Dict, Any

def record_activity(task_id: str, user_id: str, events: List[Dict[str, Any]]):
    supabase = get_supabase()
    
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    
    # Prepare batch
    records = []
    for event in events:
        records.append({
            "task_id": task_id,
            "user_id": user_id,
            "event_type": event.get("event_type"),
            "url": event.get("url"),
            "title": event.get("title"),
            "tab_id": event.get("tab_id"),
            "window_id": event.get("window_id"),
            "timestamp": event.get("timestamp"),
            "metadata": event.get("metadata")
        })
    
    if not records:
        return []

    # Insert batch
    result = supabase.table("task_activity").insert(records).execute()
    return result.data

def get_activity(task_id: str, user_id: str):
    supabase = get_supabase()
    
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
        
    result = supabase.table("task_activity").select("*").eq("task_id", task_id).eq("user_id", user_id).order("timestamp", desc=True).limit(100).execute()
    return result.data

def delete_activity(task_id: str, activity_id: str, user_id: str):
    supabase = get_supabase()
    
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
        
    result = supabase.table("task_activity").delete().eq("id", activity_id).eq("task_id", task_id).eq("user_id", user_id).execute()
    return result.data

def delete_all_activity(task_id: str, user_id: str):
    supabase = get_supabase()
    
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
        
    result = supabase.table("task_activity").delete().eq("task_id", task_id).eq("user_id", user_id).execute()
    return result.data
