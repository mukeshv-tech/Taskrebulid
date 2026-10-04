import os
import requests

url = ""
key = ""

with open("render-backend/.env", "r") as f:
    for line in f:
        if line.startswith("SUPABASE_URL="):
            url = line.strip().split("=")[1]
        elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
            key = line.strip().split("=")[1]

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

sql = """
CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_embedding vector(3072),
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
        d.user_id = p_user_id AND
        (
            (1 - (d.embedding <=> query_embedding) > match_threshold)
            OR 
            (query_text IS NOT NULL AND (d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%'))
        )
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
"""

# We can execute SQL via the REST API using a generic rpc call, but wait, there is no generic execute_sql rpc by default.
# I will just write a python script to output instructions, or I can update supabase_schema.sql and tell the user!
