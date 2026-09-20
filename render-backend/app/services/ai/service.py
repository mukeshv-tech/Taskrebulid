import logging
from fastapi import HTTPException
from typing import Any
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
                self.providers["gemini"] = GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL_NAME)
                logger.info("Gemini provider initialized.")
            except Exception as e:
                logger.error(f"Failed to init Gemini provider: {e}")

        # Initialize Groq if configured
        if settings.GROQ_API_KEY:
            try:
                from .groq_provider import GroqProvider
                self.providers["groq"] = GroqProvider(api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL_NAME)
                logger.info("Groq provider initialized.")
            except Exception as e:
                logger.error(f"Failed to init Groq provider: {e}")

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.TASK_AI_PROVIDER, self.placeholder)
        if provider == self.placeholder and settings.TASK_AI_PROVIDER in self.providers:
            pass # placeholder means it fell back
        elif not provider:
             provider = self.placeholder

        try:
            result = await provider.analyze_task(input_data)
            return result
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

    async def analyze_graph(self, input_data: AIAnalysisInput) -> Any:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.GRAPH_AI_PROVIDER, self.placeholder)

        try:
            result = await provider.analyze_graph(input_data)
            return result
        except Exception as e:
            logger.error(f"AI graph analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI graph analysis failed: {e}")

ai_service = AIService()
