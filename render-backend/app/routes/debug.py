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

@router.get("/api/debug/test-gemini")
async def test_gemini():
    try:
        from app.services.search_indexer import search_indexer
        import google.generativeai as genai
        
        if not search_indexer.provider:
            return {"status": "error", "message": "Gemini API provider not initialized. Check GEMINI_API_KEY in .env"}
            
        test_text = "Hello world"
        embedding, chunks = search_indexer.provider.generate_embedding(test_text)
        
        # also test inserting it into supabase
        from app.supabase import get_supabase
        supabase = get_supabase()
        
        return {
            "status": "success",
            "model_used": search_indexer.provider.model,
            "dimensions_generated": len(embedding),
            "first_5_values": embedding[:5],
            "last_5_values": embedding[-5:],
            "chunks_used": chunks
        }
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
