import codecs

path = 'render-backend/app/routes/graph.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if "generate_learning_path" not in content:
    route_func = """
@router.post("/api/tasks/{task_id}/learning-path")
async def generate_task_learning_path(task_id: str, user = Depends(get_current_user)):
    from app.supabase import get_supabase
    from app.services.ai.service import ai_service
    from app.services.graph_service import get_task_graph
    
    supabase = get_supabase()
    
    # 1. Verify ownership & get task name
    task_res = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_res.data or task_res.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized or task not found")
        
    task_name = task_res.data[0]["name"]
    
    # 2. Get Graph Data
    graph_data = get_task_graph(task_id, user.id)
    if not graph_data or not graph_data.get('nodes'):
        raise HTTPException(status_code=400, detail="Not enough graph data to generate a learning path. Please run graph analysis first.")

    # 3. Call AI
    markdown_path = await ai_service.generate_learning_path(task_name, graph_data['nodes'], graph_data['edges'])
    
    # 4. Save to task_ai_analyses
    data = {
        "task_id": task_id,
        "user_id": user.id,
        "analysis_type": "learning_path",
        "result": {"markdown": markdown_path}
    }
    supabase.table("task_ai_analyses").insert(data).execute()
    
    return {"status": "success", "markdown": markdown_path}

@router.get("/api/tasks/{task_id}/learning-path")
def get_task_learning_path(task_id: str, user = Depends(get_current_user)):
    from app.supabase import get_supabase
    supabase = get_supabase()
    
    # Get the latest learning path
    res = supabase.table("task_ai_analyses").select("*").eq("task_id", task_id).eq("user_id", user.id).eq("analysis_type", "learning_path").order("created_at", desc=True).limit(1).execute()
    
    if not res.data:
        return {"markdown": null}
        
    return {"markdown": res.data[0]["result"].get("markdown")}
"""
    content = content + route_func
    # Fix 'null' literal bug in python
    content = content.replace('{"markdown": null}', '{"markdown": None}')
    with open(path, 'w', encoding='utf-8') as f: f.write(content)
