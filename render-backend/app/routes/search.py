import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.supabase import get_supabase
from app.auth import get_current_user
from app.services.search_indexer import search_indexer
import google.generativeai as genai

router = APIRouter(tags=["search"])

class ExplainRequest(BaseModel):
    query: str
    result_ids: List[str]

@router.get("/api/search")
async def search_documents(
    q: str,
    task_id: Optional[str] = None,
    match_count: int = 10,
    match_threshold: float = 0.5,
    user: dict = Depends(get_current_user)
):
    try:
        query_embedding = search_indexer.embedding_provider.generate_embedding(q)
        if not query_embedding:
            pass # Should not reach here if an exception was raised inside generate_embedding
        
        response = get_supabase().rpc(
            "hybrid_search_documents",
            {
                "query_embedding": query_embedding,
                "query_text": q,
                "match_count": match_count,
                "match_threshold": match_threshold,
                "p_user_id": user["id"]
            }
        ).execute()

        # Log search history
        get_supabase().table("search_history").insert({
            "user_id": user["id"],
            "query": q
        }).execute()

        results = response.data
        if task_id:
            results = [r for r in results if r.get("task_id") == task_id]
        
        # Group results by task
        grouped_results = {}
        for row in results:
            task_id = row["task_id"]
            if task_id not in grouped_results:
                grouped_results[task_id] = []
            grouped_results[task_id].append(row)
            
        return {"results": grouped_results, "raw": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/search/suggestions")
async def search_suggestions(
    query: str,
    limit: int = 5,
    user: dict = Depends(get_current_user)
):
    try:
        # Lightweight ILIKE search for autocomplete
        response = get_supabase().table("search_documents") \
            .select("id, title, source_type") \
            .ilike("title", f"%{query}%") \
            .eq("user_id", user["id"]) \
            .limit(limit) \
            .execute()
        
        return {"suggestions": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/search/explain")
async def explain_results(
    request: ExplainRequest,
    user: dict = Depends(get_current_user)
):
    try:
        # Fetch the documents
        response = get_supabase().table("search_documents") \
            .select("title, content, source_type") \
            .in_("id", request.result_ids) \
            .eq("user_id", user["id"]) \
            .execute()
        
        documents = response.data
        if not documents:
            return {"explanation": "No documents found or access denied."}
            
        context = "\n\n".join([f"Title: {doc['title']} (Type: {doc['source_type']})\nContent: {doc['content']}" for doc in documents])
        
        prompt = f"""
        The user searched for: "{request.query}"
        
        Here are the top search results:
        {context}
        
        Please explain briefly why these results are relevant to the user's query, highlighting the key connections. Keep it concise.
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        ai_response = model.generate_content(prompt)
        
        return {"explanation": ai_response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
