import codecs
import re

path = 'render-backend/app/routes/search.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_route = """@router.get("/api/search/suggestions")
async def search_suggestions(
    q: str,
    user = Depends(get_current_user)
):
    try:
        response = get_supabase().rpc(
            "autocomplete_search",
            {
                "query_text": q,
                "p_user_id": user.id,
                "match_count": 5
            }
        ).execute()
        return {"suggestions": [row["suggestion"] for row in response.data]}
    except Exception as e:
        print(f"Suggestions error: {e}")
        return {"suggestions": []}

"""

# Insert it before run_backfill_bg
code = code.replace("def run_backfill_bg():", new_route + "def run_backfill_bg():")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
