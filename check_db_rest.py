import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv(r"C:\Users\User\Desktop\Taskrebulid\render-backend\.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

req = urllib.request.Request(f"{url}/rest/v1/tasks?select=*", headers={"apikey": key, "Authorization": f"Bearer {key}"})
with urllib.request.urlopen(req) as response:
    tasks = json.loads(response.read())

if tasks:
    task_id = tasks[0]['id']
    print(f"Task ID: {task_id}, Name: {tasks[0]['name']}")
    
    req_r = urllib.request.Request(f"{url}/rest/v1/task_resources?select=*&task_id=eq.{task_id}", headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req_r) as response:
        res = json.loads(response.read())
    print(f"Resources: {len(res)}")
    
    req_a = urllib.request.Request(f"{url}/rest/v1/task_activity?select=*&task_id=eq.{task_id}", headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req_a) as response:
        act = json.loads(response.read())
    print(f"Activity: {len(act)}")
else:
    print("No tasks found.")
