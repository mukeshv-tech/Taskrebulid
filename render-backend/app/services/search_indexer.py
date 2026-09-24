import os
from typing import Dict, Any, List
import google.generativeai as genai
from app.supabase import get_supabase
from pydantic import BaseModel

class EmbeddingProvider:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self.model_name = "models/embedding-001"

    def generate_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise ValueError(f"Error from Gemini: {e}")


class SearchIndexer:
    def __init__(self):
        self.embedding_provider = EmbeddingProvider()

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
        embedding = self.embedding_provider.generate_embedding(text_to_embed)
        
        if not embedding:
            return False

        data = {
            "user_id": user_id,
            "task_id": task_id,
            "source_type": source_type,
            "source_id": source_id,
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding
        }

        try:
            response = get_supabase().table("search_documents").upsert(
                data, on_conflict="source_type,source_id"
            ).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error indexing document: {e}")
            return False

search_indexer = SearchIndexer()
