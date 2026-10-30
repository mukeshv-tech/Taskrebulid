from fastapi import APIRouter
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/debug/ai")
def debug_ai():
    from app.services.ai.service import ai_service
    
    import_error = False
    try:
        import google.generativeai  # noqa: F401
    except Exception as e:
        logger.error(f"Google import error: {e}")
        import_error = True
        
    init_error = False
    try:
        from app.services.ai.gemini_provider import GeminiProvider  # noqa: F401
    except Exception as e:
        logger.error(f"Provider init error: {e}")
        init_error = True
        
    return {
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "gemini_api_key_length": len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0,
        "graph_provider": settings.GRAPH_AI_PROVIDER,
        "providers_loaded": list(ai_service.providers.keys()),
        "google_import_failed": import_error,
        "provider_init_failed": init_error,
        "model_name": settings.GEMINI_MODEL_NAME
    }

@router.get("/api/debug/test-gemini")
async def test_gemini():
    try:
        from app.services.search_indexer import search_indexer
        
        if not search_indexer.provider:
            return {"status": "error", "message": "Gemini API provider not initialized"}
            
        test_text = "Hello world"
        embedding, chunks = search_indexer.provider.generate_embedding(test_text)
        
        return {
            "status": "success",
            "model_used": search_indexer.provider.model,
            "dimensions_generated": len(embedding),
            "first_5_values": embedding[:5],
            "last_5_values": embedding[-5:],
            "chunks_used": chunks
        }
    except Exception as e:
        logger.error(f"Error testing gemini: {e}", exc_info=True)
        return {"status": "error", "message": "Failed to test Gemini embedding"}
