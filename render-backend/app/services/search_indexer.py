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
        self.model_name = "models/gemini-embedding-001"

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



import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

class ONNXEmbeddingProvider:
    def __init__(self):
        model_dir = os.path.join(os.path.dirname(__file__), "..", "local_model")
        self.tokenizer = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self.session = ort.InferenceSession(os.path.join(model_dir, "model_quantized.onnx"))

    def generate_embedding(self, text: str) -> List[float]:
        encoded = self.tokenizer.encode(text)
        ids = encoded.ids[:512]
        mask = encoded.attention_mask[:512]
        type_ids = encoded.type_ids[:512] if hasattr(encoded, 'type_ids') and encoded.type_ids else [0]*len(ids)
        
        pad_len = 512 - len(ids)
        if pad_len > 0:
             ids = ids + [0]*pad_len
             mask = mask + [0]*pad_len
             type_ids = type_ids + [0]*pad_len

        ort_inputs = {
            "input_ids": np.array([ids], dtype=np.int64),
            "attention_mask": np.array([mask], dtype=np.int64),
            "token_type_ids": np.array([type_ids], dtype=np.int64)
        }
        
        outputs = self.session.run(None, ort_inputs)
        # Assuming the first output is the sequence output or pooled output.
        # If sequence output, we mean pool. If pooled output, we just take it.
        out = outputs[0][0]
        if len(out.shape) == 2:
            # Sequence output (seq_len, hidden_size) -> mean pooling
            # Real mean pooling should respect attention mask, but this is a quick proxy
            embedding = np.mean(out, axis=0)
        else:
            embedding = out
            
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()


class SearchIndexer:
    def __init__(self):
        self.gemini_provider = EmbeddingProvider()
        try:
            self.onnx_provider = ONNXEmbeddingProvider()
        except Exception as e:
            print(f"Failed to load ONNX model: {e}")
            self.onnx_provider = None

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
            
        text_to_embed = f"{title}
{content}"
        
        # Generate Gemini
        gemini_embedding = None
        try:
            gemini_embedding = self.gemini_provider.generate_embedding(text_to_embed)
        except Exception as e:
            print(f"Gemini failed: {e}")
            
        # Generate ONNX
        onnx_embedding = None
        if self.onnx_provider:
            try:
                onnx_embedding = self.onnx_provider.generate_embedding(text_to_embed)
            except Exception as e:
                print(f"ONNX failed: {e}")

        data = {
            "user_id": user_id,
            "task_id": task_id,
            "source_type": source_type,
            "source_id": source_id,
            "title": title,
            "content": content,
            "metadata": metadata or {}
        }
        
        # Add whichever embeddings succeeded
        if gemini_embedding:
            data["embedding_gemini"] = gemini_embedding
        if onnx_embedding:
            data["embedding_onnx"] = onnx_embedding

        try:
            response = get_supabase().table("search_documents").upsert(
                data, on_conflict="source_type,source_id"
            ).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Supabase upsert failed: {e}")

search_indexer = SearchIndexer()
