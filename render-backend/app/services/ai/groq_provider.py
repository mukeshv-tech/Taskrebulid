import json
import logging
from groq import AsyncGroq
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "llama3-8b-8192"):
        self.api_key = api_key
        self.model_name = model_name
        if self.api_key:
            self.client = AsyncGroq(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GROQ_API_KEY is not set. GroqProvider will fail on analysis.")

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        if not self.client:
            raise ValueError("Groq API Key is not configured.")

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
OUTPUT ONLY VALID JSON. Do not include markdown like ```json.
"""

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an API that outputs strictly valid JSON. Never include markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            
            result_text = response.choices[0].message.content
            # Cleanup any accidental markdown
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(result_text)
            
            return AIAnalysisResult(**result_json)
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    async def analyze_graph(self, input_data: AIAnalysisInput) -> AIGraphAnalysisResult:
        if not self.client:
            raise ValueError("Groq API Key is not configured.")

        # Prepare the prompt
        prompt = f"""
You are an AI assistant analyzing a user's research task to extract a knowledge graph.
Task Name: {input_data.task_name}

Resources:
{json.dumps([r.model_dump() for r in input_data.resources], indent=2)}

Recent Activity:
{json.dumps([a.model_dump() for a in input_data.activity], indent=2)}

INSTRUCTIONS:
Extract a structured knowledge graph (nodes and edges) representing the entities, concepts, and relationships found in the provided Resources and Activity.
1. Use only supplied information. Do not invent resources, facts, or URLs.
2. Deduplicate nodes. E.g., "Machine Learning" and "machine learning" should be a single node. Don't aggressively merge concepts if uncertain.
3. Node labels must be clear and concise.
4. Edge relationship types must be one of: "related_to", "about", "requires", "answers", "part_of", "references".
5. Provide evidence for edges strictly referring to the provided resource IDs or activity context. Return no relationship when evidence is insufficient.
6. Confidence must be between 0.0 and 1.0 based on the evidence strength.

Output a JSON object matching this exact structure:
{{
  "nodes": [
    {{ "label": "String", "node_type": "topic", "description": "String", "confidence": 0.95 }}
  ],
  "edges": [
    {{ "source_label": "String", "target_label": "String", "relationship_type": "related_to", "confidence": 0.85, "evidence": [ {{ "resource_id": "String or null", "reason": "String" }} ] }}
  ]
}}
OUTPUT ONLY VALID JSON. Do not include markdown like ```json.
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledge graph extractor that outputs strictly valid JSON. Never include markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            
            result_text = response.choices[0].message.content
            # Cleanup any accidental markdown
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(result_text)
            
            return AIGraphAnalysisResult(**result_json)
        except Exception as e:
            logger.error(f"Groq Graph API error: {e}")
            raise
