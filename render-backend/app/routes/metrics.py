import codecs
import os
import psutil
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.supabase import get_supabase
import time

router = APIRouter(tags=["metrics"])

start_time = time.time()

# HTML template for the beautiful dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskRebuild | System Metrics</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #000000; color: #ffffff; }
        .glass-card {
            background: #0a0a0a;
            border: 1px solid #333333;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        }
        .metric-value { font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
        
        /* Pulse animation for the live dot */
        @keyframes pulse-dot {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 255, 255, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
        }
        .live-dot {
            animation: pulse-dot 2s infinite;
        }
    </style>
</head>
<body class="min-h-screen p-8 selection:bg-white selection:text-black">
    <div class="max-w-5xl mx-auto">
        <!-- Header -->
        <header class="flex justify-between items-center mb-10 pb-6 border-b border-neutral-800">
            <div>
                <h1 class="text-3xl font-bold text-white tracking-tight">TaskRebuild Engine</h1>
                <p class="text-neutral-400 mt-1 text-sm font-medium">REAL-TIME SYSTEM TELEMETRY</p>
            </div>
            <div class="flex items-center space-x-3 bg-neutral-900 px-4 py-2 rounded-md border border-neutral-700">
                <div class="w-2.5 h-2.5 bg-white rounded-full live-dot"></div>
                <span class="text-xs font-bold text-white tracking-widest uppercase">System Online</span>
            </div>
        </header>

        <!-- Main Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            
            <!-- CPU -->
            <div class="glass-card p-6 relative overflow-hidden">
                <div class="flex justify-between items-start mb-4 relative z-10">
                    <h3 class="text-neutral-400 text-sm font-semibold uppercase tracking-wider">CPU Usage</h3>
                    <svg class="w-5 h-5 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1 relative z-10">
                    <span id="cpu-val" class="text-4xl font-bold text-white metric-value">0</span>
                    <span class="text-neutral-500 font-medium">%</span>
                </div>
                <div class="w-full bg-neutral-800 rounded-none h-1 mt-6 relative z-10">
                    <div id="cpu-bar" class="bg-white h-1 rounded-none transition-all duration-500 ease-out" style="width: 0%"></div>
                </div>
            </div>

            <!-- RAM -->
            <div class="glass-card p-6 relative">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-neutral-400 text-sm font-semibold uppercase tracking-wider">Memory (RAM)</h3>
                    <svg class="w-5 h-5 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1">
                    <span id="ram-val" class="text-4xl font-bold text-white metric-value">0</span>
                    <span class="text-neutral-500 font-medium">MB</span>
                </div>
                <p id="ram-sub" class="text-xs text-neutral-500 mt-5 font-mono">RENDER LIMIT: 512 MB</p>
            </div>

            <!-- Uptime -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-neutral-400 text-sm font-semibold uppercase tracking-wider">Uptime</h3>
                    <svg class="w-5 h-5 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1">
                    <span id="uptime-val" class="text-4xl font-bold text-white metric-value">00:00:00</span>
                </div>
                <p class="text-xs text-neutral-500 mt-5 font-mono">HH:MM:SS SINCE REBOOT</p>
            </div>

            <!-- Model -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-neutral-400 text-sm font-semibold uppercase tracking-wider">AI Engine</h3>
                    <svg class="w-5 h-5 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                </div>
                <div class="flex items-center h-full pb-6 pt-1">
                    <span id="model-val" class="text-xl font-bold text-white leading-tight">Loading...</span>
                </div>
            </div>
        </div>

        <!-- Database Stats row -->
        <h2 class="text-lg font-bold text-white mb-4 mt-12 uppercase tracking-widest text-neutral-300">Database & Knowledge Graph</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            
            <div class="glass-card p-5 flex items-center justify-between">
                <div>
                    <p class="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-1">Total Tasks</p>
                    <p id="tasks-val" class="text-3xl font-bold text-white metric-value">0</p>
                </div>
                <div class="p-3 bg-neutral-900 rounded-full border border-neutral-800 text-white">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                </div>
            </div>

            <div class="glass-card p-5 flex items-center justify-between">
                <div>
                    <p class="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-1">Graph Nodes</p>
                    <p id="nodes-val" class="text-3xl font-bold text-white metric-value">0</p>
                </div>
                <div class="p-3 bg-neutral-900 rounded-full border border-neutral-800 text-white">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"></path></svg>
                </div>
            </div>

            <div class="glass-card p-5 flex items-center justify-between">
                <div>
                    <p class="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-1">Graph Edges</p>
                    <p id="edges-val" class="text-3xl font-bold text-white metric-value">0</p>
                </div>
                <div class="p-3 bg-neutral-900 rounded-full border border-neutral-800 text-white">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                </div>
            </div>

            <div class="glass-card p-5 flex items-center justify-between">
                <div>
                    <p class="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-1">Vectors Indexed</p>
                    <p id="vectors-val" class="text-3xl font-bold text-white metric-value">0</p>
                </div>
                <div class="p-3 bg-neutral-900 rounded-full border border-neutral-800 text-white">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                </div>
            </div>

        </div>
        
        <div class="text-center mt-16 text-neutral-600 text-xs font-mono tracking-widest uppercase border-t border-neutral-900 pt-6">
            <p>Data refreshes automatically every 2 seconds</p>
        </div>
    </div>"""

@router.get("/api/metrics")
async def get_metrics(request: Request):
    # Check if the client wants HTML (like a web browser)
    accept_header = request.headers.get("accept", "")
    
    if "text/html" in accept_header:
        return HTMLResponse(content=DASHBOARD_HTML)
        
    # Otherwise return the JSON data
    try:
        supabase = get_supabase()
        
        # CPU & RAM Stats
        process = psutil.Process(os.getpid())
        ram_usage_mb = process.memory_info().rss / 1024 / 1024
        cpu_usage = psutil.cpu_percent(interval=0.1)
        uptime_seconds = time.time() - start_time
        
        # Database Stats
        doc_count = supabase.table("search_documents").select("id", count="exact").limit(1).execute()
        task_count = supabase.table("tasks").select("id", count="exact").limit(1).execute()
        node_count = supabase.table("task_nodes").select("id", count="exact").limit(1).execute()
        edge_count = supabase.table("task_edges").select("id", count="exact").limit(1).execute()
        
        return JSONResponse({
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
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
