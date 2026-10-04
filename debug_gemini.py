import codecs
import re

path = 'render-backend/app/routes/debug.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_debug_route = """
@router.get("/api/debug/test-gemini")
async def test_gemini():
    try:
        from app.services.search_indexer import search_indexer
        import google.generativeai as genai
        
        if not search_indexer.provider:
            return {"status": "error", "message": "Gemini API provider not initialized. Check GEMINI_API_KEY in .env"}
            
        test_text = "Hello world"
        embedding, chunks = search_indexer.provider.generate_embedding(test_text)
        
        # also test inserting it into supabase
        from app.supabase import get_supabase
        supabase = get_supabase()
        
        return {
            "status": "success",
            "model_used": search_indexer.provider.model,
            "dimensions_generated": len(embedding),
            "first_5_values": embedding[:5],
            "last_5_values": embedding[-5:],
            "chunks_used": chunks
        }
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
"""

code = code + "\n" + new_debug_route.strip() + "\n"

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
