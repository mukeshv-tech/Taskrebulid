import codecs

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'router = APIRouter(prefix="/api/search", tags=["search"])',
    'router = APIRouter(tags=["search"])'
)
code = code.replace('@router.get("")', '@router.get("/api/search")')
code = code.replace('@router.get("/suggestions")', '@router.get("/api/search/suggestions")')
code = code.replace('@router.post("/explain")', '@router.post("/api/search/explain")')

# Also fix the query parameter to be 'q' instead of 'query'
code = code.replace(
    '''async def search_documents(
    query: str,
    match_count: int = 10,''',
    '''async def search_documents(
    q: str,
    task_id: Optional[str] = None,
    match_count: int = 10,'''
)
code = code.replace('generate_embedding(query)', 'generate_embedding(q)')
code = code.replace('"query_text": query', '"query_text": q')
code = code.replace('"query": query', '"query": q')
# Also filter by task_id if provided
code = code.replace('results = response.data', '''results = response.data
        if task_id:
            results = [r for r in results if r.get("task_id") == task_id]''')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
