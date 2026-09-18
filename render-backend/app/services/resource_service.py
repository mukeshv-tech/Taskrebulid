from app.supabase import get_supabase

def create_resource(task_id: str, user_id: str, url: str, title: str):
    supabase = get_supabase()
    
    # Verify task exists and belongs to user
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
        
    # Check for duplicate
    existing = supabase.table("task_resources").select("id").eq("task_id", task_id).eq("url", url).execute()
    if existing.data:
        raise ValueError("Resource already exists in this task")
        
    result = supabase.table("task_resources").insert({
        "task_id": task_id,
        "user_id": user_id,
        "url": url,
        "title": title
    }).execute()
    
    return result.data[0]

def list_resources(task_id: str, user_id: str):
    supabase = get_supabase()
    # RLS handles user_id, but good practice to explicitly query with it
    # We should still verify the task belongs to the user
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
        
    result = supabase.table("task_resources").select("*").eq("task_id", task_id).eq("user_id", user_id).execute()
    return result.data

def delete_resource(task_id: str, resource_id: str, user_id: str):
    supabase = get_supabase()
    # Verify resource belongs to user and task
    resource = supabase.table("task_resources").select("id").eq("id", resource_id).eq("task_id", task_id).eq("user_id", user_id).execute()
    if not resource.data:
        raise ValueError("Resource not found or not owned by user")
        
    supabase.table("task_resources").delete().eq("id", resource_id).execute()
