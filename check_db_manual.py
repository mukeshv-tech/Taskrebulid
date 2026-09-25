import urllib.request
import json
import re

env_content = open(r"C:\Users\User\Desktop\Taskrebulid\render-backend\.env").read()
url = re.search(r"SUPABASE_URL=(.*)", env_content).group(1).strip()
key = re.search(r"SUPABASE_SERVICE_ROLE_KEY=(.*)", env_content).group(1).strip()

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
