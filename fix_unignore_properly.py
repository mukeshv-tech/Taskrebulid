import re

path = 'render-backend/app/services/resource_monitor.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# I will replace the whole block
pattern = r"update_data = \{[\s\S]*?\}\s*if content_hash:"
replacement = """update_data = {
            'check_status': check_status,
            'last_checked_at': datetime.utcnow().isoformat(),
            'is_ignored': False
        }
        
        if content_hash:"""

code = re.sub(pattern, replacement, code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
