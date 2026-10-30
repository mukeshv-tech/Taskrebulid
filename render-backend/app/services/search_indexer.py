from typing import Dict, Any
from app.config import settings
from app.supabase import get_supabase

class GeminiEmbeddingProvider:
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = "gemini-embedding-001"

    def generate_embedding(self, text: str):
        if not text.strip():
            # Return dummy 3072 dim vector just in case, though it shouldn't happen
            return ([0.0] * 3072, 1)
            
        try:
            import google.generativeai as genai
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document",
            )
            embedding = result['embedding']
            
            # If the model surprisingly returns something other than 3072 dimensions, 
            # pad or truncate it to EXACTLY 3072 dimensions to satisfy PostgreSQL!
            if len(embedding) < 3072:
                embedding = embedding + [0.0] * (3072 - len(embedding))
            elif len(embedding) > 3072:
                embedding = embedding[:3072]
                
            return (embedding, 1)
        except Exception as e:
            print(f"Gemini embedding failed: {e}")
            return ([0.0] * 3072, 1)

class SearchIndexer:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.provider = GeminiEmbeddingProvider(api_key=settings.GEMINI_API_KEY)
        else:
            self.provider = None

    def index_document(
        self,
        user_id: str,
        task_id: str,
        source_type: str,
        source_id: str,
        title: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        if not content and not title:
            return False
            
        text_to_embed = f"{title}\n{content}"
        
        if not self.provider:
            raise Exception("Gemini API key not found, embedding provider not loaded")
            
        embedding, chunks_used = self.provider.generate_embedding(text_to_embed)
        
        meta = metadata or {}
        meta["chunks_used"] = chunks_used

        data = {
            "user_id": user_id,
            "task_id": task_id,
            "source_type": source_type,
            "source_id": source_id,
            "title": title,
            "content": content,
            "metadata": meta,
            "embedding": embedding
        }

        try:
            get_supabase().table("search_documents").upsert(
                data, on_conflict="source_type,source_id"
            ).execute()
            return True
        except Exception as e:
            print(f"Index document error: {e}")
            return False

search_indexer = SearchIndexer()
