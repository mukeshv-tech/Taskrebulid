import codecs
import re

path = 'render-backend/app/services/search_indexer.py'
code = codecs.open(path, 'r', 'utf-8').read()

new_class = """
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
"""

code = re.sub(
    r'class ONNXEmbeddingProvider:.*?return embedding\.tolist\(\)',
    new_class.strip(),
    code,
    flags=re.DOTALL
)

# update index_document to receive tuple
new_index = """
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
"""
code = re.sub(
    r'if not self\.onnx_provider:.*?\"embedding\": embedding\n\s+\}',
    new_index.strip(),
    code,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
