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
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .metric-value { font-variant-numeric: tabular-nums; }
        
        /* Pulse animation for the live dot */
        @keyframes pulse-dot {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        .live-dot {
            animation: pulse-dot 2s infinite;
        }
    </style>
</head>
<body class="min-h-screen p-8 selection:bg-indigo-500 selection:text-white">
    <div class="max-w-5xl mx-auto">
        <!-- Header -->
        <header class="flex justify-between items-center mb-10">
            <div>
                <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">TaskRebuild Engine</h1>
                <p class="text-slate-400 mt-1">Real-time system telemetry & AI status</p>
            </div>
            <div class="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700">
                <div class="w-3 h-3 bg-emerald-500 rounded-full live-dot"></div>
                <span class="text-sm font-medium text-emerald-400 tracking-wide uppercase">System Online</span>
            </div>
        </header>

        <!-- Main Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            
            <!-- CPU -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-slate-400 font-medium">CPU Usage</h3>
                    <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1">
                    <span id="cpu-val" class="text-4xl font-bold text-white metric-value">0</span>
                    <span class="text-slate-400 font-medium">%</span>
                </div>
                <div class="w-full bg-slate-700 rounded-full h-1.5 mt-4">
                    <div id="cpu-bar" class="bg-blue-400 h-1.5 rounded-full transition-all duration-500 ease-out" style="width: 0%"></div>
                </div>
            </div>

            <!-- RAM -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-slate-400 font-medium">Memory (RAM)</h3>
                    <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1">
                    <span id="ram-val" class="text-4xl font-bold text-white metric-value">0</span>
                    <span class="text-slate-400 font-medium">MB</span>
                </div>
                <p id="ram-sub" class="text-xs text-slate-500 mt-4">Render Free Tier Limit: 512 MB</p>
            </div>

            <!-- Uptime -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-slate-400 font-medium">Server Uptime</h3>
                    <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1">
                    <span id="uptime-val" class="text-4xl font-bold text-white metric-value">00:00:00</span>
                </div>
                <p class="text-xs text-slate-500 mt-4">HH:MM:SS since last reboot</p>
            </div>

            <!-- Model -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-slate-400 font-medium">AI Engine</h3>
                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                </div>
                <div class="flex items-center h-full pb-6">
                    <span id="model-val" class="text-lg font-bold text-white leading-tight">Loading...</span>
                </div>
            </div>
        </div>

        <!-- Database Stats row -->
        <h2 class="text-xl font-semibold text-white mb-4 mt-10 border-b border-slate-700 pb-2">Database Graph & Indexing</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            
            <div class="glass-card p-5 flex items-center space-x-4">
                <div class="p-3 bg-slate-800 rounded-lg border border-slate-700">
                    <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                </div>
                <div>
                    <p class="text-sm text-slate-400">Total Tasks</p>
                    <p id="tasks-val" class="text-2xl font-bold text-white metric-value">0</p>
                </div>
            </div>

            <div class="glass-card p-5 flex items-center space-x-4">
                <div class="p-3 bg-slate-800 rounded-lg border border-slate-700">
                    <svg class="w-6 h-6 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"></path></svg>
                </div>
                <div>
                    <p class="text-sm text-slate-400">Graph Nodes</p>
                    <p id="nodes-val" class="text-2xl font-bold text-white metric-value">0</p>
                </div>
            </div>

            <div class="glass-card p-5 flex items-center space-x-4">
                <div class="p-3 bg-slate-800 rounded-lg border border-slate-700">
                    <svg class="w-6 h-6 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                </div>
                <div>
                    <p class="text-sm text-slate-400">Graph Edges</p>
                    <p id="edges-val" class="text-2xl font-bold text-white metric-value">0</p>
                </div>
            </div>

            <div class="glass-card p-5 flex items-center space-x-4">
                <div class="p-3 bg-slate-800 rounded-lg border border-slate-700">
                    <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                </div>
                <div>
                    <p class="text-sm text-slate-400">Vectors Indexed</p>
                    <p id="vectors-val" class="text-2xl font-bold text-white metric-value">0</p>
                </div>
            </div>

        </div>
        
        <div class="text-center mt-12 text-slate-600 text-sm">
            <p>Data refreshes automatically every 2 seconds.</p>
        </div>
    </div>

    <script>
        function formatUptime(seconds) {
            const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
            const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
            const s = Math.floor(seconds % 60).toString().padStart(2, '0');
            return `${h}:${m}:${s}`;
        }

        async function fetchMetrics() {
            try {
                // Fetch JSON data by sending application/json accept header
                const response = await fetch('/api/metrics', {
                    headers: { 'Accept': 'application/json' }
                });
                const data = await response.json();

                if(data.error) {
                    console.error("API Error:", data.error);
                    return;
                }

                // Update UI
                document.getElementById('cpu-val').innerText = data.server.cpu_usage_percent.toFixed(1);
                document.getElementById('cpu-bar').style.width = `${Math.min(100, data.server.cpu_usage_percent)}%`;
                
                document.getElementById('ram-val').innerText = data.server.ram_usage_mb;
                
                document.getElementById('uptime-val').innerText = formatUptime(data.server.uptime_seconds);
                document.getElementById('model-val').innerText = data.server.model_loaded;

                document.getElementById('tasks-val').innerText = data.database.total_tasks;
                document.getElementById('nodes-val').innerText = data.database.knowledge_graph_nodes;
                document.getElementById('edges-val').innerText = data.database.knowledge_graph_edges;
                document.getElementById('vectors-val').innerText = data.database.indexed_search_documents;

            } catch (err) {
                console.error("Failed to fetch metrics", err);
            }
        }

        // Fetch immediately, then every 2 seconds
        fetchMetrics();
        setInterval(fetchMetrics, 2000);
    </script>
</body>
</html>
"""

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
