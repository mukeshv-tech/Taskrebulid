import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
    TASK_AI_PROVIDER: str = os.getenv("TASK_AI_PROVIDER", "gemini")
    GRAPH_AI_PROVIDER: str = os.getenv("GRAPH_AI_PROVIDER", "gemini")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-120b")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-3.6-flash")
    AI_MAX_INPUT_TOKENS: int = int(os.getenv("AI_MAX_INPUT_TOKENS", 4096))
    AI_MAX_OUTPUT_TOKENS: int = int(os.getenv("AI_MAX_OUTPUT_TOKENS", 1024))
    AI_ACTIVITY_LIMIT: int = int(os.getenv("AI_ACTIVITY_LIMIT", 100))
    AI_RESOURCE_LIMIT: int = int(os.getenv("AI_RESOURCE_LIMIT", 50))
    RESUME_AI_PROVIDER: str = os.getenv("RESUME_AI_PROVIDER", "gemini")
    AI_RESUME_MAX_ACTIVITY: int = int(os.getenv("AI_RESUME_MAX_ACTIVITY", 50))
    AI_RESUME_MAX_RESOURCES: int = int(os.getenv("AI_RESUME_MAX_RESOURCES", 30))
    AI_RESUME_MAX_GRAPH_NODES: int = int(os.getenv("AI_RESUME_MAX_GRAPH_NODES", 30))
    AI_RESUME_MAX_GRAPH_EDGES: int = int(os.getenv("AI_RESUME_MAX_GRAPH_EDGES", 30))
    AI_RESUME_MAX_SNAPSHOTS: int = int(os.getenv("AI_RESUME_MAX_SNAPSHOTS", 5))
    PORT: int = int(os.getenv("PORT", 8000))

    class Config:
        env_file = ".env"

settings = Settings()
