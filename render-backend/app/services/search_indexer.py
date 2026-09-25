import os
from typing import Dict, Any, List
from app.supabase import get_supabase
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
        out = outputs[0][0]
        if len(out.shape) == 2:
            embedding = np.mean(out, axis=0)
        else:
            embedding = out
            
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()

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
            
        embedding = self.onnx_provider.generate_embedding(text_to_embed)

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
            raise Exception(f"Supabase upsert failed: {e}")

search_indexer = SearchIndexer()
