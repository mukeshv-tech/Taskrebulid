import codecs
import re

path = 'taskrebuild/extension/src/popup/components/SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

# Make the <li> have a cursor pointer and an onClick handler
old_li = "<li key={item.id} style={{ background: 'white', padding: '10px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>"
new_li = """<li 
                      key={item.id} 
                      onClick={() => {
                        if (onNavigateToTask) {
                          onNavigateToTask(item.task_id);
                        }
                      }}
                      style={{ background: 'white', padding: '10px', borderRadius: '4px', border: '1px solid #e2e8f0', cursor: 'pointer', transition: 'background 0.2s' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                    >"""

code = code.replace(old_li, new_li)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
