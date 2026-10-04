from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, auth, tasks, resources, activity, ai, graph, resume, monitoring, search, debug, metrics

from app.config import settings



from contextlib import asynccontextmanager
import asyncio
from app.services.cron_monitor import run_cron_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the backend cron job
    cron_task = asyncio.create_task(run_cron_monitor())
    yield
    cron_task.cancel()

from fastapi.responses import HTMLResponse


description = """
# Welcome to the TaskRebuild API 🚀

TaskRebuild is an intelligent, context-aware productivity backend that automatically tracks your browsing activity, captures resources, and maps your workflow into an advanced vector-searchable Knowledge Graph.

## Core Engines
* **Google-Clone RRF Search**: A 3072-dimension semantic search engine powered by Gemini AI, merged with PostgreSQL Trigrams and Full-Text Reciprocal Rank Fusion.
* **Knowledge Graph**: Every task, resource, and browser session is mapped into a dynamic graph to help you understand how your workflows connect.
* **Live System Metrics**: Asynchronous, zero-latency monitoring of RAM, Python runtime, and vector counts.

### Getting Started
Use the interactive client on the right to instantly test any endpoint. All requests require your Supabase Auth JWT token in the `Authorization: Bearer` header.
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
        <!-- Inject Scalar API Reference -->
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





# CORS setup

origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else []



app.add_middleware(

    CORSMiddleware,

    allow_origins=origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



app.include_router(health.router)

app.include_router(auth.router)

app.include_router(tasks.router)

app.include_router(resources.router)

app.include_router(activity.router)

app.include_router(ai.router)

app.include_router(graph.router)
app.include_router(debug.router)
app.include_router(metrics.router)

app.include_router(resume.router)

app.include_router(monitoring.router)
app.include_router(search.router)

