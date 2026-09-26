import os
from typing import Dict, Any, List
from app.supabase import get_supabase
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

class ONNXEmbeddingProvider:
    def __init__(self):
        import os
        model_dir = os.path.join(os.path.dirname(__file__), "..", "local_model")
        self.tokenizer = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self.session = ort.InferenceSession(os.path.join(model_dir, "model_quantized.onnx"))

    def generate_embedding(self, text: str):
        encoded = self.tokenizer.encode(text)
        all_ids = encoded.ids
        all_mask = encoded.attention_mask
        all_type_ids = encoded.type_ids if hasattr(encoded, 'type_ids') and encoded.type_ids else [0]*len(all_ids)
        
        chunk_size = 512
        max_chunks = 10
        embeddings = []
        
        total_chunks = min( (len(all_ids) + chunk_size - 1) // chunk_size, max_chunks )
        if total_chunks == 0:
            total_chunks = 1
            
        for i in range(0, total_chunks * chunk_size, chunk_size):
            ids = all_ids[i:i+chunk_size]
            mask = all_mask[i:i+chunk_size]
            type_ids = all_type_ids[i:i+chunk_size]
            
            if not ids:
                break
                
            pad_len = chunk_size - len(ids)
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
            out = outputs[0][0]
            if len(out.shape) == 2:
                emb = np.mean(out, axis=0)
            else:
                emb = out
            embeddings.append(emb)
            
        if not embeddings:
            return ([0.0] * 384, 0)
            
        avg_embedding = np.mean(embeddings, axis=0)
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm
            
        return (avg_embedding.tolist(), total_chunks)

class SearchIndexer:
    def __init__(self):
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
            
        text_to_embed = f"{title}\n{content}"
        
        if not self.onnx_provider:
            raise Exception("ONNX model is not loaded")
            
        embedding, chunks_used = self.onnx_provider.generate_embedding(text_to_embed)
        
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
            response = get_supabase().table("search_documents").upsert(
                data, on_conflict="source_type,source_id"
            ).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Supabase upsert failed: {e}")

search_indexer = SearchIndexer()
