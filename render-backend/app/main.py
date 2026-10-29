import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from app.routes import health, auth, tasks, resources, activity, ai, graph, resume, monitoring, search, debug, metrics, clusters, knowledge
from app.config import settings

from contextlib import asynccontextmanager
import asyncio
from app.services.cron_monitor import run_cron_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    cron_task = asyncio.create_task(run_cron_monitor())
    yield
    cron_task.cancel()

description = """
# Welcome to the TaskRebuild API 🚀

TaskRebuild is an intelligent, context-aware productivity backend that automatically tracks your browsing activity, captures resources, and maps your workflow into an advanced vector-searchable Knowledge Graph and Personal Knowledge System.
"""

app = FastAPI(
    title="TaskRebuild API", 
    version="2.0.0",
    description=description,
    lifespan=lifespan, 
    docs_url=None, 
    redoc_url=None
)

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TaskRebuild API - Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <script 
            id="api-reference" 
            data-url="{app.openapi_url}" 
            data-theme="moon"
            data-layout="modern"
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
    </body>
    </html>
    """
    return HTMLResponse(html)

origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(resources.router)
app.include_router(activity.router)
app.include_router(ai.router)
app.include_router(graph.router)
app.include_router(debug.router)
app.include_router(metrics.router)
app.include_router(clusters.router)
app.include_router(resume.router)
app.include_router(monitoring.router)
app.include_router(search.router)
app.include_router(knowledge.router)
app.include_router(knowledge.task_router)

# Static Frontend Assets & Primary Root Web Page
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_homepage():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"status": "ok", "message": "TaskRebuild API"}
