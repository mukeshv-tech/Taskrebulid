import codecs
import re

path = 'render-backend/app/routes/metrics.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_python_code = """
        # New System Metrics
        disk_usage = psutil.disk_usage('/').percent
        
        # Try to read Docker/cgroup memory limit instead of host RAM
        total_ram_bytes = None
        try:
            # cgroup v2
            if os.path.exists('/sys/fs/cgroup/memory.max'):
                with open('/sys/fs/cgroup/memory.max', 'r') as f:
                    val = f.read().strip()
                    if val != 'max': total_ram_bytes = int(val)
            # cgroup v1
            elif os.path.exists('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
                with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                    total_ram_bytes = int(f.read().strip())
        except: pass
        
        if total_ram_bytes and total_ram_bytes < psutil.virtual_memory().total:
            total_ram_gb = round(total_ram_bytes / (1024**3), 2)
        else:
            total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)

        active_threads = process.num_threads()
"""

# Replace the old logic
code = re.sub(
    r'# New System Metrics.*?active_threads = process.num_threads\(\)',
    new_python_code.strip(),
    code,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
