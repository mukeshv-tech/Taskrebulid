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

        # Initialize Local if configured
        if settings.MODEL_PATH:
            try:
                from .local_model import LocalModelProvider
                self.providers["local"] = LocalModelProvider(settings.MODEL_NAME, settings.MODEL_PATH)
                logger.info("Local provider initialized.")
            except Exception as e:
                logger.error(f"Failed to init Local provider: {e}")

    async def analyze_task(self, input_data: AIAnalysisInput, provider_choice: str = None) -> AIAnalysisResult:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        # Use requested provider, fallback to default in settings, or placeholder
        choice = provider_choice or settings.AI_PROVIDER
        provider = self.providers.get(choice)
        
        if not provider:
            logger.warning(f"Provider '{choice}' not available. Using placeholder.")
            provider = self.placeholder

        try:
            result = await provider.analyze_task(input_data)
            return result
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

ai_service = AIService()
