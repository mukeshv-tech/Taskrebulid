import codecs
import re

path = r'C:\Users\User\Desktop\Taskrebulid\taskrebuild\extension\src\popup\components\SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

new_form = """      <div style={{ position: 'relative', marginBottom: '15px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            onFocus={() => { if(suggestions.length > 0) setShowSuggestions(true); }}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Keywords or semantic question..."
            style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
          />
          <button type="submit" disabled={loading} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        {showSuggestions && suggestions.length > 0 && (
          <ul style={{ 
            position: 'absolute', top: '100%', left: 0, right: '70px', 
            background: 'white', border: '1px solid #e2e8f0', borderRadius: '4px', 
            listStyle: 'none', padding: 0, margin: '4px 0 0 0', 
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', zIndex: 50 
          }}>
            {suggestions.map((sug, idx) => (
              <li 
                key={idx}
                onMouseDown={(e) => {
                  e.preventDefault();
                  setQuery(sug);
                  setShowSuggestions(false);
                }}
                style={{ padding: '8px 12px', fontSize: '13px', cursor: 'pointer', borderBottom: idx === suggestions.length - 1 ? 'none' : '1px solid #f1f5f9' }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
              >
                {sug}
              </li>
            ))}
          </ul>
        )}
      </div>"""

# Replace the old form with the new one
old_form = """      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px', marginBottom: '15px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Keywords or semantic question..."
          style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
        />
        <button type="submit" disabled={loading} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>"""

code = code.replace(old_form, new_form)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
