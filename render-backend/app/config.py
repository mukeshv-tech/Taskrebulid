import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    AI_MAX_INPUT_TOKENS: int = int(os.getenv("AI_MAX_INPUT_TOKENS", 4096))
    AI_MAX_OUTPUT_TOKENS: int = int(os.getenv("AI_MAX_OUTPUT_TOKENS", 1024))
    AI_ACTIVITY_LIMIT: int = int(os.getenv("AI_ACTIVITY_LIMIT", 50))
    AI_RESOURCE_LIMIT: int = int(os.getenv("AI_RESOURCE_LIMIT", 20))
    PORT: int = int(os.getenv("PORT", 8000))

    class Config:
        env_file = ".env"

settings = Settings()
