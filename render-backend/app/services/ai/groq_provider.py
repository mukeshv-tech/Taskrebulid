import json
import logging
from groq import AsyncGroq
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "llama3-70b-8192"):
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

        prompt = f"""
Analyze the following research task and provide insights.
Task Name: {input_data.task_name}
Resources: {json.dumps([r.model_dump() for r in input_data.resources])}
Recent Activity: {json.dumps([a.model_dump() for a in input_data.activity])}
"""
        schema_json = json.dumps(AIAnalysisResult.model_json_schema())

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that outputs strictly in JSON. The JSON object must strictly follow this schema: {schema_json}"
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
            
            raw_text = response.choices[0].message.content
            result_json = json.loads(raw_text)
            return AIAnalysisResult(**result_json)
        except json.JSONDecodeError:
            raise ValueError(f"Model failed to generate valid JSON. Raw output: {raw_text}")
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    async def analyze_graph(self, input_data: AIAnalysisInput) -> AIGraphAnalysisResult:
        if not self.client:
            raise ValueError("Groq API Key is not configured.")

        prompt = f"""
Extract a structured knowledge graph (nodes and edges) representing the entities, concepts, and relationships found in the provided Resources and Activity.
Task Name: {input_data.task_name}
Resources: {json.dumps([r.model_dump() for r in input_data.resources])}
Recent Activity: {json.dumps([a.model_dump() for a in input_data.activity])}

1. Use only supplied information.
2. Deduplicate nodes.
3. Edge relationship types must be one of: "related_to", "about", "requires", "answers", "part_of", "references".
4. Confidence must be between 0.0 and 1.0.
"""
        schema_json = json.dumps(AIGraphAnalysisResult.model_json_schema())

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a knowledge graph extractor that outputs strictly in JSON. The JSON object must strictly follow this schema: {schema_json}"
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
            
            raw_text = response.choices[0].message.content
            result_json = json.loads(raw_text)
            return AIGraphAnalysisResult(**result_json)
        except json.JSONDecodeError:
            raise ValueError(f"Model failed to generate valid JSON. Raw output: {raw_text}")
        except Exception as e:
            logger.error(f"Groq Graph API error: {e}")
            raise
