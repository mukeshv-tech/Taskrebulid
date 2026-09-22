import codecs
import re

path = 'taskrebuild/extension/src/popup/components/ResourceMonitor.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace("triggerResourceCheck,", "triggerResourceCheck, toggleResourceIgnore,")

handler = """
  const handleToggleIgnore = async (resourceId: string) => {
    try {
      await toggleResourceIgnore(taskId, resourceId);
      await fetchResources();
    } catch (err: any) {
      console.error(err);
      alert('Toggle ignore failed: ' + err.message);
    }
  };
"""

code = code.replace("const handleCheckNow = async", handler + "\n  const handleCheckNow = async")

button = """
              <button 
                onClick={() => handleToggleIgnore(r.id)} 
                style={{ height: '24px', fontSize: '10px', padding: '0 8px', background: 'white', border: '1px solid #d1d5db', borderRadius: '4px', cursor: 'pointer', flexShrink: 0, marginLeft: '10px', color: r.is_ignored ? '#2563eb' : '#4b5563' }}
              >
                {r.is_ignored ? 'Unignore' : 'Ignore'}
              </button>
              <button 
"""

code = code.replace("<button \n                onClick={() => handleCheckNow(r.id)}", button + "                onClick={() => handleCheckNow(r.id)}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
