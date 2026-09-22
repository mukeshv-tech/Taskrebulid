import codecs

path = 'render-backend/app/services/resource_monitor.py'
code = codecs.open(path, 'r', 'utf-8').read()

old_str = "'last_checked_at': datetime.utcnow().isoformat()"
new_str = "'last_checked_at': datetime.utcnow().isoformat(),\n            'is_ignored': False"

code = code.replace(old_str, new_str)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
