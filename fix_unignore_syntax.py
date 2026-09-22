import codecs
import re

path = 'render-backend/app/services/resource_monitor.py'
code = codecs.open(path, 'r', 'utf-8').read()

# I need to restore the }
code = code.replace("'is_ignored': False", "'is_ignored': False\n        }")
code = code.replace("False\n        }\n\n        if content_hash:", "False\n        }\n        if content_hash:")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
