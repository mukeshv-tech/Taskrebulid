import time
import os
import psutil
import json

def run_benchmark():
    try:
        from llama_cpp import Llama
    except ImportError:
        print("llama_cpp not installed yet.")
        return

    model_path = "qwen2-0_5b-instruct-q4_k_m.gguf"
    if not os.path.exists(model_path):
        print(f"Model {model_path} not found.")
        return

    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024

    print(f"Loading model {model_path}...")
    start_time = time.time()
    
    # Load model with minimal context for CPU constraints
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=2,
        verbose=False
    )
    
    load_time = time.time() - start_time
    mem_after = process.memory_info().rss / 1024 / 1024
    mem_used = mem_after - mem_before
    
    print(f"Startup Time: {load_time:.2f}s")
    print(f"RAM Used: {mem_used:.2f}MB")

    prompt = """<|im_start|>system
You are a helpful AI assistant. Analyze the following browser activity and resources for a task, and output a JSON object describing the task.
Output exactly this JSON structure and nothing else:
{
  "task_summary": "Summary text",
  "topics": [{"name": "topic", "confidence": 0.9}],
  "resource_analysis": [{"resource_id": "r1", "relevance": 0.8, "reason": "reason"}],
  "activity_summary": "Summary of activities",
  "suggested_next_steps": ["step 1", "step 2"]
}
<|im_end|>
<|im_start|>user
Task Name: Learn React
Resources:
- r1: https://react.dev
Activity:
- Searched Google for "react tutorial"
- Opened https://react.dev/learn
<|im_end|>
<|im_start|>assistant
"""
    
    print("Running inference...")
    start_inf = time.time()
    
    response = llm(
        prompt,
        max_tokens=300,
        stop=["<|im_end|>"],
        temperature=0.1
    )
    
    inf_time = time.time() - start_inf
    
    output = response["choices"][0]["text"]
    
    print(f"Inference Latency: {inf_time:.2f}s")
    print("Raw Output:")
    print(output)
    
    try:
        parsed = json.loads(output)
        print("JSON Reliability: SUCCESS")
        print("Parsed JSON:")
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print(f"JSON Reliability: FAILED - {e}")

if __name__ == "__main__":
    run_benchmark()
