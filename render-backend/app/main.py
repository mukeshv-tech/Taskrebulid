from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, auth, tasks, resources, activity, ai, graph, resume, monitoring, search

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

app = FastAPI(title="TaskRebuild Backend", lifespan=lifespan)




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

app.include_router(resume.router)

app.include_router(monitoring.router)
app.include_router(search.router)

