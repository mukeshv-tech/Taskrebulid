import codecs
import re

path = r'C:\Users\User\Desktop\Taskrebulid\taskrebuild\extension\src\popup\components\SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

# 1. Add copiedId state and handleCopyLink function
state_addition = """  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopyLink = async (e: React.MouseEvent, url: string, id: string) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(url);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error("Copy failed", err);
      alert("Failed to copy link");
    }
  };
"""
code = code.replace("const [error, setError] = useState<string | null>(null);", "const [error, setError] = useState<string | null>(null);\n" + state_addition)

# 2. Add the Copy button next to the Open Resource button
old_button = """                        {item.url && (
                          <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '10px', padding: '4px 8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', textDecoration: 'none', color: '#0f172a' }}>
                            Open Resource
                          </a>
                        )}"""

new_buttons = """                        {item.url && (
                          <a href={item.url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} style={{ fontSize: '10px', padding: '4px 8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', textDecoration: 'none', color: '#0f172a' }}>
                            Open Resource
                          </a>
                        )}
                        {item.url && (
                          <button 
                            onClick={(e) => handleCopyLink(e, item.url!, item.id)} 
                            style={{ 
                              fontSize: '10px', 
                              padding: '4px 8px', 
                              background: copiedId === item.id ? '#dcfce7' : '#f1f5f9', 
                              color: copiedId === item.id ? '#166534' : '#0f172a', 
                              border: '1px solid', 
                              borderColor: copiedId === item.id ? '#bbf7d0' : '#cbd5e1', 
                              borderRadius: '4px', 
                              cursor: 'pointer', 
                              transition: 'all 0.2s' 
                            }}
                          >
                            {copiedId === item.id ? '✓ Copied!' : 'Copy Link'}
                          </button>
                        )}"""

code = code.replace(old_button, new_buttons)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
