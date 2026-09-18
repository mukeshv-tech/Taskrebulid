import logging
from fastapi import HTTPException
from app.config import settings
from .interface import AIProvider
from .local_model import LocalModelProvider
from .placeholder import PlaceholderAIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.provider = self._init_provider()

    def _init_provider(self) -> AIProvider:
        if not settings.AI_ENABLED:
            return PlaceholderAIProvider()
        if settings.AI_PROVIDER == "gemini":
            from .gemini_provider import GeminiProvider
            return GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.MODEL_NAME)
        if settings.AI_PROVIDER == "local":
            return LocalModelProvider(settings.MODEL_NAME, settings.MODEL_PATH)
        return PlaceholderAIProvider()

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        try:
            result = await self.provider.analyze_task(input_data)
            return result
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise HTTPException(status_code=500, detail="AI analysis failed.")

ai_service = AIService()
