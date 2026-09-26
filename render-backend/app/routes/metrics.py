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
    <title>TaskRebuild | System Telemetry</title>
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
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="flex justify-between items-center mb-10 pb-6 border-b border-neutral-800">
            <div>
                <h1 class="text-3xl font-bold text-white tracking-tight">TaskRebuild Engine</h1>
                <p class="text-neutral-400 mt-1 text-sm font-medium uppercase tracking-widest" id="python-ver">REAL-TIME SYSTEM TELEMETRY</p>
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
                <p id="ram-sub" class="text-xs text-neutral-500 mt-5 font-mono uppercase tracking-widest">Total System RAM: <span id="ram-total">0</span> GB</p>
            </div>

            <!-- Disk -->
            <div class="glass-card p-6 relative overflow-hidden">
                <div class="flex justify-between items-start mb-4 relative z-10">
                    <h3 class="text-neutral-400 text-sm font-semibold uppercase tracking-wider">Disk Storage</h3>
                    <svg class="w-5 h-5 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1 relative z-10">
                    <span id="disk-val" class="text-4xl font-bold text-white metric-value">0</span>
                    <span class="text-neutral-500 font-medium">%</span>
                </div>
                <div class="w-full bg-neutral-800 rounded-none h-1 mt-6 relative z-10">
                    <div id="disk-bar" class="bg-white h-1 rounded-none transition-all duration-500 ease-out" style="width: 0%"></div>
                </div>
            </div>

            <!-- Uptime -->
            <div class="glass-card p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-neutral-400 text-sm font-semibold uppercase tracking-wider">Uptime & Threads</h3>
                    <svg class="w-5 h-5 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <div class="flex items-baseline space-x-1">
                    <span id="uptime-val" class="text-3xl font-bold text-white metric-value">00:00:00</span>
                </div>
                <p class="text-xs text-neutral-500 mt-6 font-mono uppercase tracking-widest"><span id="threads-val">0</span> Active Threads</p>
            </div>
        </div>

        <!-- Database Stats row -->
        <h2 class="text-lg font-bold text-white mb-4 mt-12 uppercase tracking-widest text-neutral-300">Database Engine Metrics</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            
            <div class="glass-card p-5 flex flex-col items-center justify-center text-center">
                <p class="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">Tasks</p>
                <p id="tasks-val" class="text-3xl font-bold text-white metric-value">0</p>
            </div>

            <div class="glass-card p-5 flex flex-col items-center justify-center text-center">
                <p class="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">URLs Saved</p>
                <p id="resources-val" class="text-3xl font-bold text-white metric-value">0</p>
            </div>

            <div class="glass-card p-5 flex flex-col items-center justify-center text-center">
                <p class="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">Browser Logs</p>
                <p id="activity-val" class="text-3xl font-bold text-white metric-value">0</p>
            </div>

            <div class="glass-card p-5 flex flex-col items-center justify-center text-center">
                <p class="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">Graph Nodes</p>
                <p id="nodes-val" class="text-3xl font-bold text-white metric-value">0</p>
            </div>

            <div class="glass-card p-5 flex flex-col items-center justify-center text-center">
                <p class="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">Graph Edges</p>
                <p id="edges-val" class="text-3xl font-bold text-white metric-value">0</p>
            </div>

            <div class="glass-card p-5 flex flex-col items-center justify-center text-center">
                <p class="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">Vectors</p>
                <p id="vectors-val" class="text-3xl font-bold text-white metric-value">0</p>
            </div>

        </div>

        <div class="mt-8 glass-card p-4 flex justify-between items-center">
            <span class="text-xs text-neutral-400 font-mono tracking-widest uppercase">EMBEDDING MODEL</span>
            <span id="model-val" class="text-sm font-bold text-white tracking-widest uppercase">Loading...</span>
        </div>
        
        <div class="text-center mt-12 text-neutral-600 text-[10px] font-mono tracking-widest uppercase border-t border-neutral-900 pt-6">
            <p>Data refreshes automatically every 1 second</p>
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
                const response = await fetch('/api/metrics', {
                    headers: { 'Accept': 'application/json' }
                });
                const data = await response.json();

                if(data.error) {
                    console.error("API Error:", data.error);
                    return;
                }

                document.getElementById('cpu-val').innerText = data.server.cpu_usage_percent.toFixed(1);
                document.getElementById('cpu-bar').style.width = `${Math.min(100, data.server.cpu_usage_percent)}%`;
                
                document.getElementById('ram-val').innerText = data.server.ram_usage_mb;
                document.getElementById('ram-total').innerText = data.server.total_ram_gb;
                
                document.getElementById('disk-val').innerText = data.server.disk_usage_percent.toFixed(1);
                document.getElementById('disk-bar').style.width = `${Math.min(100, data.server.disk_usage_percent)}%`;

                document.getElementById('uptime-val').innerText = formatUptime(data.server.uptime_seconds);
                document.getElementById('threads-val').innerText = data.server.active_threads;
                document.getElementById('python-ver').innerText = `REAL-TIME TELEMETRY • PYTHON ${data.server.python_version}`;

                document.getElementById('model-val').innerText = data.server.model_loaded;

                document.getElementById('tasks-val').innerText = data.database.total_tasks;
                document.getElementById('resources-val').innerText = data.database.total_resources;
                document.getElementById('activity-val').innerText = data.database.total_activity;
                document.getElementById('nodes-val').innerText = data.database.knowledge_graph_nodes;
                document.getElementById('edges-val').innerText = data.database.knowledge_graph_edges;
                document.getElementById('vectors-val').innerText = data.database.indexed_search_documents;

            } catch (err) {
                console.error("Failed to fetch metrics", err);
            }
        }

        fetchMetrics();
        setInterval(fetchMetrics, 1000);
    </script>
</body>
</html>
"""

@router.get("/api/metrics")
async def get_metrics(request: Request):
    accept_header = request.headers.get("accept", "")
    
    if "text/html" in accept_header:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=DASHBOARD_HTML)
        
    try:
        from fastapi.responses import JSONResponse
        import sys
        supabase = get_supabase()
        
        process = psutil.Process(os.getpid())
        ram_usage_mb = process.memory_info().rss / 1024 / 1024
        cpu_usage = psutil.cpu_percent(interval=0.1)
        uptime_seconds = time.time() - start_time
        
        # New System Metrics
        disk_usage = psutil.disk_usage('/').percent
        
        # Try to read Docker/cgroup memory limit instead of host RAM
        total_ram_bytes = None
        try:
            # cgroup v2
            if os.path.exists('/sys/fs/cgroup/memory.max'):
                with open('/sys/fs/cgroup/memory.max', 'r') as f:
                    val = f.read().strip()
                    if val != 'max': total_ram_bytes = int(val)
            # cgroup v1
            elif os.path.exists('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
                with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                    total_ram_bytes = int(f.read().strip())
        except: pass
        
        if total_ram_bytes and total_ram_bytes < psutil.virtual_memory().total:
            total_ram_gb = round(total_ram_bytes / (1024**3), 2)
        else:
            total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)

        active_threads = process.num_threads()
        python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Database Stats
        doc_count = supabase.table("search_documents").select("id", count="exact").limit(1).execute()
        task_count = supabase.table("tasks").select("id", count="exact").limit(1).execute()
        res_count = supabase.table("task_resources").select("id", count="exact").limit(1).execute()
        act_count = supabase.table("task_activity").select("id", count="exact").limit(1).execute()
        node_count = supabase.table("task_nodes").select("id", count="exact").limit(1).execute()
        edge_count = supabase.table("task_edges").select("id", count="exact").limit(1).execute()
        
        return JSONResponse({
            "server": {
                "ram_usage_mb": round(ram_usage_mb, 2),
                "total_ram_gb": total_ram_gb,
                "cpu_usage_percent": cpu_usage,
                "disk_usage_percent": disk_usage,
                "uptime_seconds": int(uptime_seconds),
                "active_threads": active_threads,
                "python_version": python_ver,
                "model_loaded": "ONNX bge-small-en-v1.5 (Local)"
            },
            "database": {
                "total_tasks": task_count.count if task_count else 0,
                "total_resources": res_count.count if res_count else 0,
                "total_activity": act_count.count if act_count else 0,
                "indexed_search_documents": doc_count.count if doc_count else 0,
                "knowledge_graph_nodes": node_count.count if node_count else 0,
                "knowledge_graph_edges": edge_count.count if edge_count else 0
            }
        })
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
