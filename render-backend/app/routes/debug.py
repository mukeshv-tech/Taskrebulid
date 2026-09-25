import os
from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/api/debug/ai")
def debug_ai():
    from app.services.ai.service import ai_service
    
    # Try importing manually to catch the exact error
    import_error = None
    try:
        import google.generativeai as genai
    except Exception as e:
        import_error = str(e)
        
    init_error = None
    try:
        from app.services.ai.gemini_provider import GeminiProvider
    except Exception as e:
        init_error = str(e)
        
    return {
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "gemini_api_key_length": len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0,
        "graph_provider": settings.GRAPH_AI_PROVIDER,
        "providers_loaded": list(ai_service.providers.keys()),
        "google_import_error": import_error,
        "provider_init_error": init_error,
        "model_name": settings.GEMINI_MODEL_NAME
    }
