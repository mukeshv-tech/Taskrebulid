import json
import logging
import google.generativeai as genai
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.model_name = model_name
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logger.warning("GEMINI_API_KEY is not set. GeminiProvider will fail on analysis.")

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

        # Prepare the prompt
        prompt = f"""
You are an AI assistant analyzing a user's research task.
Task Name: {input_data.task_name}

Resources:
{json.dumps([r.model_dump() for r in input_data.resources], indent=2)}

Recent Activity:
{json.dumps([a.model_dump() for a in input_data.activity], indent=2)}

Based ONLY on the provided resources and activity, analyze the task and return a JSON object with the following schema:
{{
  "task_summary": "A brief summary of what this task is about based on the data",
  "topics": [
    {{ "name": "Topic Name", "confidence": 0.95 }}
  ],
  "resource_analysis": [
    {{ "resource_id": "id from the resource object", "relevance": 0.8, "reason": "why it's relevant" }}
  ],
  "activity_summary": "A brief summary of the user's recent actions",
  "suggested_next_steps": [
    "Step 1", "Step 2"
  ]
}}
Do not invent resources. Keep confidence values between 0.0 and 1.0.
Respond strictly in valid JSON without markdown wrapping like ```json.
"""

        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            
            result_text = response.text
            result_json = json.loads(result_text)
            
            return AIAnalysisResult(**result_json)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
