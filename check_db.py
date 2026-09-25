import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(r"C:\Users\User\Desktop\Taskrebulid\render-backend\.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

# Get one task
tasks = supabase.table("tasks").select("*").limit(1).execute()
if tasks.data:
    task_id = tasks.data[0]['id']
    print(f"Task ID: {task_id}, Name: {tasks.data[0]['name']}")
    
    res = supabase.table("task_resources").select("*").eq("task_id", task_id).execute()
    print(f"Resources: {len(res.data)}")
    
    act = supabase.table("task_activity").select("*").eq("task_id", task_id).execute()
    print(f"Activity: {len(act.data)}")
else:
    print("No tasks found.")
