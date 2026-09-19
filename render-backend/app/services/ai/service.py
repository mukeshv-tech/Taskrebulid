import logging
from fastapi import HTTPException
from app.config import settings
from .interface import AIProvider
from .placeholder import PlaceholderAIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.providers = {}
        self.placeholder = PlaceholderAIProvider()
        self._init_providers()

    def _init_providers(self):
        # Initialize Gemini if configured
        if settings.GEMINI_API_KEY:
            try:
                from .gemini_provider import GeminiProvider
                self.providers["gemini"] = GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.MODEL_NAME)
                logger.info("Gemini provider initialized.")
            except Exception as e:
                logger.error(f"Failed to init Gemini provider: {e}")

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.AI_PROVIDER, self.placeholder)

        try:
            result = await provider.analyze_task(input_data)
            return result
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

ai_service = AIService()
