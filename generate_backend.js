const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'render-backend');

const files = {
  'requirements.txt': `fastapi==0.110.0
uvicorn==0.27.1
supabase==2.3.6
pydantic==2.6.3
python-dotenv==1.0.1
pydantic-settings==2.2.1
`,
  '.env.example': `SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
ALLOWED_ORIGINS=http://localhost:5173,chrome-extension://your-extension-id
AI_ENABLED=false
AI_PROVIDER=placeholder
MODEL_PATH=
PORT=8000
`,
  '.gitignore': `__pycache__/
*.pyc
.env
.venv/
venv/
`,
  'render.yaml': `services:
  - type: web
    name: taskrebuild-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: ALLOWED_ORIGINS
        sync: false
      - key: AI_ENABLED
        value: "false"
      - key: AI_PROVIDER
        value: "placeholder"
`,
  'README.md': `# TaskRebuild Render Backend
This is the backend API for TaskRebuild.

## Deployment to Render
1. Connect this repo to Render.
2. Select the \`render-backend\` folder as the root directory.
3. Build Command: \`pip install -r requirements.txt\`
4. Start Command: \`uvicorn app.main:app --host 0.0.0.0 --port $PORT\`
`,
  'app/__init__.py': ``,
  'app/config.py': `import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "placeholder")
    PORT: int = int(os.getenv("PORT", 8000))

    class Config:
        env_file = ".env"

settings = Settings()
`,
  'app/supabase.py': `from supabase import create_client, Client
from app.config import settings

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
`,
  'app/auth.py': `from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase import get_supabase
import logging

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase = get_supabase()
    try:
        user_resp = supabase.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_resp.user
    except Exception as e:
        logging.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
`,
  'app/routes/__init__.py': ``,
  'app/routes/health.py': `from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
`,
  'app/routes/auth.py': `from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.get("/api/me")
def get_me(user = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
`,
  'app/routes/tasks.py': `from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.auth import get_current_user
from app.supabase import get_supabase

router = APIRouter()

class TaskCreate(BaseModel):
    name: str

@router.get("/api/tasks")
def list_tasks(user = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("tasks").select("*").eq("user_id", user.id).execute()
    return result.data

@router.post("/api/tasks")
def create_task(task: TaskCreate, user = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("tasks").insert({"user_id": user.id, "name": task.name}).execute()
    if len(result.data) > 0:
        return result.data[0]
    raise HTTPException(status_code=500, detail="Failed to create task")

@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, user = Depends(get_current_user)):
    supabase = get_supabase()
    # Check ownership
    task = supabase.table("tasks").select("user_id").eq("id", task_id).execute()
    if not task.data or task.data[0]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    supabase.table("tasks").delete().eq("id", task_id).execute()
    return {"status": "deleted"}
`,
  'app/services/__init__.py': ``,
  'app/services/ai/__init__.py': ``,
  'app/services/ai/interface.py': `from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def process(self, input_text: str) -> str:
        pass
`,
  'app/services/ai/placeholder.py': `from app.services.ai.interface import AIProvider

class PlaceholderAI(AIProvider):
    def process(self, input_text: str) -> str:
        return f"Processed: {input_text} (AI is disabled)"
`,
  'app/main.py': `from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, auth, tasks
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
`
};

function ensureDirSync(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

for (const [relativePath, content] of Object.entries(files)) {
  const fullPath = path.join(basePath, relativePath);
  ensureDirSync(path.dirname(fullPath));
  fs.writeFileSync(fullPath, content, 'utf8');
}
console.log('Backend files generated.');
