import json
import logging
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, Topic, ResourceAnalysis

logger = logging.getLogger(__name__)

class LocalModelProvider(AIProvider):
    def __init__(self, model_name: str, model_path: str):
        self.model_name = model_name
        self.model_path = model_path
        self.llm = None
        
        # Load the model once at service startup
        if self.model_path:
            try:
                from llama_cpp import Llama
                logger.info(f"Loading local model {self.model_name} from {self.model_path}")
                # We use a constrained context size suitable for free CPU limits
                self.llm = Llama(
                    model_path=self.model_path,
                    n_ctx=2048,
                    n_threads=2, # Optimized for 1-2 vCPU instances like Render Free
                    verbose=False
                )
                logger.info("Local model loaded successfully.")
            except ImportError:
                logger.error("llama-cpp-python is not installed. Run pip install llama-cpp-python")
            except Exception as e:
                logger.error(f"Failed to load local model from {self.model_path}: {e}")

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not self.llm:
            raise ValueError("Local model is not loaded. Ensure MODEL_PATH is correct and llama-cpp-python is installed.")

        # Construct prompt for the instruction model (assuming ChatML format like Qwen)
        resources_json = json.dumps([r.model_dump() for r in input_data.resources], indent=2)
        activity_json = json.dumps([a.model_dump() for a in input_data.activity], indent=2)
        
        prompt = f"""<|im_start|>system
You are an AI analyzing a user's research task. Output exactly this JSON structure:
{{
  "task_summary": "string",
  "topics": [{{"name": "string", "confidence": 0.9}}],
  "resource_analysis": [{{"resource_id": "string", "relevance": 0.8, "reason": "string"}}],
  "activity_summary": "string",
  "suggested_next_steps": ["string"]
}}
<|im_end|>
<|im_start|>user
Task Name: {input_data.task_name}
Resources:
{resources_json}
Activity:
{activity_json}
<|im_end|>
<|im_start|>assistant
{{"""

        try:
            # We enforce JSON structure via prompt engineering and appending a starting `{`
            response = self.llm(
                prompt,
                max_tokens=1024,
                stop=["<|im_end|>"],
                temperature=0.1
            )
            
            output_text = "{" + response["choices"][0]["text"]
            
            # Simple cleanup in case the model adds extra tokens
            if "```json" in output_text:
                output_text = output_text.replace("```json", "").replace("```", "").strip()
                
            result_json = json.loads(output_text)
            return AIAnalysisResult(**result_json)
        except json.JSONDecodeError as e:
            logger.error(f"Model output JSON decoding failed: {e}. Output was: {output_text}")
            raise ValueError("Local model failed to produce valid JSON.")
        except Exception as e:
            logger.error(f"Local model inference failed: {e}")
            raise
