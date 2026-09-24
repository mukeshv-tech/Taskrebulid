import codecs

path = 'render-backend/app/services/search_indexer.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'return []',
    'raise ValueError(f"Error from Gemini: {e}")'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

path2 = 'render-backend/app/routes/search.py'
code2 = codecs.open(path2, 'r', 'utf-8').read()

code2 = code2.replace(
    'raise HTTPException(status_code=500, detail="Failed to generate query embedding")',
    'pass # Should not reach here if an exception was raised inside generate_embedding'
)

with open(path2, 'w', encoding='utf-8') as f:
    f.write(code2)
