import codecs
import os
import psutil
from fastapi import APIRouter
from app.supabase import get_supabase
import time

router = APIRouter(tags=["metrics"])

start_time = time.time()

@router.get("/api/metrics")
async def get_metrics():
    try:
        supabase = get_supabase()
        
        # CPU & RAM Stats
        process = psutil.Process(os.getpid())
        ram_usage_mb = process.memory_info().rss / 1024 / 1024
        cpu_usage = psutil.cpu_percent(interval=0.1)
        uptime_seconds = time.time() - start_time
        
        # Database Stats (Count rows)
        # Using exact=True to get the count
        doc_count = supabase.table("search_documents").select("id", count="exact").limit(1).execute()
        task_count = supabase.table("tasks").select("id", count="exact").limit(1).execute()
        node_count = supabase.table("task_nodes").select("id", count="exact").limit(1).execute()
        edge_count = supabase.table("task_edges").select("id", count="exact").limit(1).execute()
        
        return {
            "server": {
                "ram_usage_mb": round(ram_usage_mb, 2),
                "cpu_usage_percent": cpu_usage,
                "uptime_seconds": int(uptime_seconds),
                "model_loaded": "ONNX bge-small-en-v1.5 (Local)"
            },
            "database": {
                "total_tasks": task_count.count if task_count else 0,
                "indexed_search_documents": doc_count.count if doc_count else 0,
                "knowledge_graph_nodes": node_count.count if node_count else 0,
                "knowledge_graph_edges": edge_count.count if edge_count else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}
