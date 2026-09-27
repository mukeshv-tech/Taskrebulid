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
    match_threshold: float = 0.75,
    user = Depends(get_current_user)
):
    try:
        query_embedding, _ = search_indexer.onnx_provider.generate_embedding(q)
        if not query_embedding:
            pass # Should not reach here if an exception was raised inside generate_embedding
        
        response = get_supabase().rpc(
            "hybrid_search_documents",
            {
                "query_embedding": query_embedding,
                "query_text": q,
                "match_count": match_count,
                "match_threshold": match_threshold,
                "p_user_id": user.id
            }
        ).execute()

        # Log search history
        get_supabase().table("search_history").insert({
            "user_id": user.id,
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



from fastapi import BackgroundTasks
import time

def run_backfill_bg():
    try:
        from app.supabase import get_supabase
        from app.services.search_indexer import search_indexer
        supabase = get_supabase()
        tasks = supabase.table("tasks").select("*").execute()
        resources = supabase.table("task_resources").select("*").execute()
        
        # Paginate activities if huge
        activities = supabase.table("task_activity").select("*").execute()
        
        # Index tasks
        if tasks.data:
            for task in tasks.data:
                try:
                    search_indexer.index_document(
                        user_id=task.get("user_id"),
                        task_id=task.get("id"),
                        source_type="task",
                        source_id=task.get("id"),
                        title=task.get("name") or "Untitled",
                        content=task.get("description", "") or ""
                    )
                except Exception as e:
                    print(f"Backfill indexing error: {e}")
                time.sleep(0.2) # Yield CPU to prevent freezing server

        # Index resources
        if resources.data:
            for res in resources.data:
                try:
                    search_indexer.index_document(
                        user_id=res.get("user_id"),
                        task_id=res.get("task_id"),
                        source_type="resource",
                        source_id=res.get("id"),
                        title=res.get("title") or res.get("url") or "Untitled",
                        content=f"{res.get('description', '')} \n {res.get('url', '')}"
                    )
                except Exception as e:
                    print(f"Backfill indexing error: {e}")
                time.sleep(0.2)

        # Index activities
        if activities.data:
            for act in activities.data:
                if not act.get("title") and not act.get("url"):
                    continue
                try:
                    search_indexer.index_document(
                        user_id=act.get("user_id"),
                        task_id=act.get("task_id"),
                        source_type="activity",
                        source_id=act.get("id"),
                        title=act.get("title") or "Browser Activity",
                        content=act.get("url") or ""
                    )
                except Exception as e:
                    print(f"Backfill indexing error: {e}")
                time.sleep(0.2)
    except Exception as e:
        print(f"Backfill failed: {e}")

@router.get("/api/search/backfill")
async def backfill_search_documents(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_backfill_bg)
    return {"status": "success", "message": "Backfill has been started in the background. Check your /api/metrics dashboard in a few minutes to see the Vectors count increase!"}
