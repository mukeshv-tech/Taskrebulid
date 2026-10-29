import logging
from fastapi import HTTPException
from typing import Any, Dict, List
from app.config import settings
from .interface import AIProvider
from .placeholder import PlaceholderAIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIResumeInput, AIResumeResult

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
                self.groq_error = str(e)
                logger.error(f"Failed to init Groq provider: {e}")

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.TASK_AI_PROVIDER, self.placeholder)
        if provider == self.placeholder:
            keys_set = []
            if settings.GEMINI_API_KEY: keys_set.append("GEMINI")
            if settings.GROQ_API_KEY: keys_set.append("GROQ")
            groq_err = getattr(self, 'groq_error', 'None')
            debug_msg = f"Placeholder AI. Requested: {settings.TASK_AI_PROVIDER}. Loaded: {list(self.providers.keys())}. Keys Set: {keys_set}. Groq Error: {groq_err}"
            return AIAnalysisResult(
                task_summary=debug_msg,
                topics=[], resource_analysis=[], activity_summary=debug_msg, suggested_next_steps=[]
            )

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

    async def analyze_resume(self, input_data: Any) -> Any:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.RESUME_AI_PROVIDER, self.placeholder)
        if provider == self.placeholder and settings.RESUME_AI_PROVIDER in self.providers:
            pass
        elif not provider:
             provider = self.placeholder

        try:
            result = await provider.analyze_resume(input_data)
            return result
        except Exception as e:
            logger.error(f"AI resume analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI resume analysis failed: {e}")

    async def analyze_replacement(self, original_resource: dict, task_name: str, existing_resources: list, task_graph: dict) -> Any:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get('groq', self.placeholder)
        if not provider:
             provider = self.placeholder

        try:
            result = await provider.analyze_replacement(original_resource, task_name, existing_resources, task_graph)
            return result
        except Exception as e:
            logger.error(f"AI replacement analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI replacement analysis failed: {e}")

    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.GRAPH_AI_PROVIDER, self.placeholder)
        if not provider:
             provider = self.placeholder

        try:
            return await provider.generate_learning_path(task_name, nodes, edges)
        except Exception as e:
            logger.error(f"AI learning path generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI learning path failed: {e}")

    async def suggest_knowledge(self, task_data: Dict[str, Any], existing_knowledge: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Suggests knowledge items and relationships based on task content, falling back safely."""
        if not settings.AI_ENABLED:
            return await self.placeholder.suggest_knowledge(task_data, existing_knowledge)

        preferred = settings.TASK_AI_PROVIDER or 'gemini'
        provider = self.providers.get(preferred)
        
        if not provider:
            # Fall back to any available configured provider, or placeholder
            for p in self.providers.values():
                provider = p
                break

        if not provider:
            provider = self.placeholder

        try:
            raw_result = await provider.suggest_knowledge(task_data, existing_knowledge)
            return raw_result
        except Exception as e:
            logger.warning(f"AI provider {provider} suggest_knowledge failed: {e}. Falling back to placeholder.")
            return await self.placeholder.suggest_knowledge(task_data, existing_knowledge)

ai_service = AIService()
