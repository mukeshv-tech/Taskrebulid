import os
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
