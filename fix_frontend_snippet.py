import codecs

path = r'C:\Users\User\Desktop\Taskrebulid\taskrebuild\extension\src\popup\components\SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

old_snippet = """<p style={{ margin: '6px 0', fontSize: '12px', color: '#334155', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {item.snippet}
                      </p>"""

new_snippet = """<p 
                        style={{ margin: '6px 0', fontSize: '12px', color: '#334155', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
                        dangerouslySetInnerHTML={{ __html: item.snippet || item.content || '' }}
                      />"""

# wait, the original code doesn't have exactly this formatting
# I will use a regex replace
import re
new_code = re.sub(
    r"<p style=\{\{ margin: '6px 0', fontSize: '12px', color: '#334155', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' \}\}>\s*\{item\.snippet\}\s*</p>",
    new_snippet,
    code
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_code)
