import codecs
import re

path = 'supabase_schema.sql'
code = codecs.open(path, 'r', 'utf-8').read()

old_func = """CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_embedding vector(768),
    query_text text,
    match_count int,
    match_threshold float
)
RETURNS TABLE (
    id uuid,
    task_id uuid,
    source_type text,
    source_id uuid,
    title text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS 
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.task_id,
        d.source_type,
        d.source_id,
        d.title,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM search_documents d
    WHERE 
        (auth.uid() = d.user_id) AND
        (1 - (d.embedding <=> query_embedding) > match_threshold) AND
        (query_text IS NULL OR d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%')
    ORDER BY similarity DESC
    LIMIT match_count;
END;
;"""

new_func = """CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_embedding vector(768),
    query_text text,
    match_count int,
    match_threshold float,
    p_user_id uuid
)
RETURNS TABLE (
    id uuid,
    task_id uuid,
    source_type text,
    source_id uuid,
    title text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.task_id,
        d.source_type,
        d.source_id,
        d.title,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM search_documents d
    WHERE 
        (d.user_id = p_user_id) AND
        (1 - (d.embedding <=> query_embedding) > match_threshold) AND
        (query_text IS NULL OR d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%')
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;"""

code = code.replace(old_func, new_func)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
