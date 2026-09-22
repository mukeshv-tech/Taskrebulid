import re

path = 'taskrebuild/extension/src/popup/components/ResourceMonitor.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

button_code = """
              <button 
                onClick={() => handleToggleIgnore(r.id)} 
                style={{ height: '24px', fontSize: '10px', padding: '0 8px', background: 'white', border: '1px solid #d1d5db', borderRadius: '4px', cursor: 'pointer', flexShrink: 0, marginLeft: '10px', color: r.is_ignored ? '#2563eb' : '#4b5563' }}
              >
                {r.is_ignored ? 'Unignore' : 'Ignore'}
              </button>
              <button 
                onClick={() => handleCheckNow(r.id)}"""

code = re.sub(r'<\s*button\s+onClick=\{\(\)\s*=>\s*handleCheckNow\(r\.id\)\}', button_code, code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
