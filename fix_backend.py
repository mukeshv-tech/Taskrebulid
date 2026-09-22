import re

path = 'render-backend/app/routes/monitoring.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix get_resource_status
get_status_pattern = r'@router\.get\("/api/tasks/\{task_id\}/resources/status"\)\s*def get_resource_status\(task_id: str, user=Depends\(get_current_user\)\):\s*try:\s*supabase = get_supabase\(\)\s*response = supabase\.table\(\'task_resources\'\)\.select\(\'\*\'\)\.eq\(\'task_id\', task_id\)\.eq\(\'user_id\', user\.id\)\.execute\(\)\s*return \{"resources": response\.data\}'

get_status_replacement = '''@router.get("/api/tasks/{task_id}/resources/status")
def get_resource_status(task_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        task_resp = supabase.table('tasks').select('auto_monitor_enabled').eq('id', task_id).eq('user_id', user.id).execute()
        auto_monitor = task_resp.data[0].get('auto_monitor_enabled', False) if task_resp.data else False
        
        response = supabase.table('task_resources').select('*').eq('task_id', task_id).eq('user_id', user.id).execute()
        return {"resources": response.data, "auto_monitor_enabled": auto_monitor}'''

code = re.sub(get_status_pattern, get_status_replacement, code, flags=re.MULTILINE)

# Fix dismiss_alert
dismiss_pattern = r'@router\.post\("/api/tasks/\{task_id\}/resources/\{resource_id\}/dismiss-alert"\)\s*def dismiss_alert\(task_id: str, resource_id: str, user=Depends\(get_current_user\)\):\s*try:\s*supabase = get_supabase\(\)\s*supabase\.table\(\'task_resources\'\)\.update\(\{\'check_status\': \'available\'\}\)\.eq\(\'id\', resource_id\)\.eq\(\'user_id\', user\.id\)\.execute\(\)\s*return \{"status": "success"\}'

dismiss_replacement = '''@router.post("/api/tasks/{task_id}/resources/{resource_id}/dismiss-alert")
def dismiss_alert(task_id: str, resource_id: str, user=Depends(get_current_user)):
    try:
        supabase = get_supabase()
        supabase.table('task_resources').update({'check_status': 'available', 'is_ignored': True}).eq('id', resource_id).eq('user_id', user.id).execute()
        return {"status": "success"}'''

code = re.sub(dismiss_pattern, dismiss_replacement, code, flags=re.MULTILINE)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
