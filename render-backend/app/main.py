from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, auth, tasks, resources, activity, ai, graph
from app.config import settings

app = FastAPI(title="TaskRebuild Backend")

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
