import codecs
import re

path = r'C:\Users\User\Desktop\Taskrebulid\taskrebuild\extension\src\popup\components\SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'dangerouslySetInnerHTML={{ __html: item.snippet || item.content || \'\' }}',
    'dangerouslySetInnerHTML={{ __html: item.snippet || \'\' }}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
