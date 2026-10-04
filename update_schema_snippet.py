import codecs
import re

path = 'supabase_schema.sql'
code = codecs.open(path, 'r', 'utf-8').read()

# Replace RETURNS TABLE content with snippet
code = code.replace(
    'content text,\n    metadata jsonb,',
    'snippet text,\n    metadata jsonb,'
)

# Replace the output in the final SELECT
old_select = """    SELECT 
        d.id,
        d.task_id,
        d.source_type,
        d.source_id,
        d.title,
        d.content,
        d.metadata,"""

new_select = """    SELECT 
        d.id,
        d.task_id,
        d.source_type,
        d.source_id,
        d.title,
        ts_headline(
            'english', 
            coalesce(d.title, '') || ' ' || coalesce(d.content, ''), 
            plainto_tsquery('english', query_text), 
            'StartSel = <mark style="background-color: #fef08a; padding: 0 2px; border-radius: 2px; font-weight: bold;">, StopSel = </mark>, MaxWords=35, MinWords=15, ShortWord=3, HighlightAll=FALSE, MaxFragments=2, FragmentDelimiter=" ... "'
        ) AS snippet,
        d.metadata,"""

code = code.replace(old_select, new_select)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
