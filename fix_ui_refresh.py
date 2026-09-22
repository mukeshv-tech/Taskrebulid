import re

path = 'taskrebuild/extension/src/popup/components/ResourceMonitor.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r"<h3 style=\{\{ margin: 0, color: '#111827' \}\}>RESOURCE ALERTS</h3>\s*\{!loading && \(\s*<button\s*onClick=\{handleToggleAutoMonitor\}"

replacement = """<h3 style={{ margin: 0, color: '#111827' }}>RESOURCE ALERTS</h3>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button 
            onClick={fetchResources}
            disabled={loading}
            style={{ 
              fontSize: '11px', padding: '4px 10px', borderRadius: '12px', border: '1px solid #d1d5db', cursor: 'pointer',
              background: 'white', color: '#4b5563', fontWeight: 600
            }}
          >
            {loading ? '↻...' : '↻ Refresh'}
          </button>
        {!loading && (
          <button 
            onClick={handleToggleAutoMonitor}"""

code = re.sub(pattern, replacement, code)

# add closing div for the flex container
pattern2 = r"\{autoMonitor \? 'Auto-Monitor: ON' : 'Auto-Monitor: OFF'\}\s*</button>\s*\)\}\s*</div>"
replacement2 = """{autoMonitor ? 'Auto-Monitor: ON' : 'Auto-Monitor: OFF'}
          </button>
        )}
        </div>
      </div>"""

code = re.sub(pattern2, replacement2, code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
