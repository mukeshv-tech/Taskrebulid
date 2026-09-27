import codecs
import re

path = 'render-backend/app/routes/debug.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_debug = """
@router.get("/api/debug/fix-vector")
async def fix_vector_db():
    try:
        from app.supabase import get_supabase
        supabase = get_supabase()
        
        # We need to use RPC to execute raw SQL to alter the table
        # But if we don't have a raw SQL executor RPC, we can just drop the table and recreate it?
        # Actually, let's just try to call a raw SQL function if it exists, otherwise return instructions
        return {
            "error": "To fix this, you must run this exact SQL command in your Supabase SQL Editor:",
            "sql": "ALTER TABLE public.search_documents ALTER COLUMN embedding TYPE vector(384); DROP FUNCTION IF EXISTS hybrid_search_documents; CREATE OR REPLACE FUNCTION hybrid_search_documents(query_embedding vector(384), query_text text, match_count int, match_threshold float, p_user_id uuid) RETURNS TABLE (id uuid, task_id uuid, source_type text, source_id uuid, title text, content text, metadata jsonb, similarity float) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY SELECT d.id, d.task_id, d.source_type, d.source_id, d.title, d.content, d.metadata, 1 - (d.embedding <=> query_embedding) AS similarity FROM search_documents d WHERE (d.user_id = p_user_id) AND (1 - (d.embedding <=> query_embedding) > match_threshold) AND (query_text IS NULL OR d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%') ORDER BY similarity DESC LIMIT match_count; END; $$;"
        }
    except Exception as e:
        return {"error": str(e)}
"""

code = code + "\n" + new_debug.strip() + "\n"

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
