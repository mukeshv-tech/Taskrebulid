import codecs
import re

path = 'render-backend/app/main.py'
code = codecs.open(path, 'r', 'utf-8').read()

lifespan_code = '''from contextlib import asynccontextmanager
import asyncio
from app.services.cron_monitor import run_cron_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the backend cron job
    cron_task = asyncio.create_task(run_cron_monitor())
    yield
    cron_task.cancel()

app = FastAPI(title="TaskRebuild Backend", lifespan=lifespan)
'''

code = code.replace('app = FastAPI(title="TaskRebuild Backend")', lifespan_code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
