import json
import logging
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult, AIResumeInput, AIResumeResult

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-120b"):
        self.api_key = api_key
        self.model_name = model_name
        if self.api_key:
            from groq import AsyncGroq
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

    async def analyze_resume(self, input_data: AIResumeInput) -> AIResumeResult:
        if not self.client:
            raise ValueError("Groq API Key is not configured.")

        schema_json = json.dumps(AIResumeResult.model_json_schema())

        prompt = f"""
You are an AI assistant helping a user resume a past task.
Task Name: {input_data.task_name}

Resources:
{json.dumps(input_data.resources, indent=2)}

Activity:
{json.dumps(input_data.activity, indent=2)}

Latest AI Analysis:
{json.dumps(input_data.latest_analysis, indent=2) if input_data.latest_analysis else "None"}

Previous Snapshot:
{json.dumps(input_data.previous_snapshot, indent=2) if input_data.previous_snapshot else "None"}

INSTRUCTIONS:
Analyze the provided history and generate a structured summary of where the user left off.
Do not invent facts, resources, or URLs. If insufficient information, explicitly state it.
Provide important URLs directly from the recent Activity that the user should reopen to continue their task.

Output must be valid JSON matching this schema exactly:
{schema_json}
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise data analysis assistant. Output only valid JSON matching the requested schema exactly, with no additional text or markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content
            result_json = json.loads(raw_text)
            return AIResumeResult(**result_json)
        except json.JSONDecodeError:
            raise ValueError(f"Model failed to generate valid JSON. Raw output: {raw_text}")
        except Exception as e:
            logger.error(f"Groq Resume API error: {e}")
            raise

    async def analyze_replacement(self, original_resource: dict, task_name: str, existing_resources: list, task_graph: dict, existing_activity: list = None):
        if not self.client:
            raise ValueError("Groq API Key is not configured.")

        from .schemas import ReplacementAnalysisResult
        schema_json = json.dumps(ReplacementAnalysisResult.model_json_schema())

        prompt = f"""
You are an AI assistant helping a user find a replacement for a broken resource.
Task Name: {task_name}

Broken Resource:
{json.dumps(original_resource, indent=2)}

Existing Task Resources:
{json.dumps(existing_resources, indent=2)}

Recent Task Activity:
{json.dumps(existing_activity, indent=2) if existing_activity else 'None'}

Task Graph:
{json.dumps(task_graph, indent=2) if task_graph else 'None'}

INSTRUCTIONS:
Analyze the broken resource, the existing resources, and the recent task activity. 
Suggest up to 3 resources (from Existing Task Resources or Recent Task Activity) that could serve as a good replacement or alternative for the broken resource.
IMPORTANT: If you suggest a resource from Recent Task Activity, use its URL as the resource_id!
Output must be valid JSON matching this schema exactly:
{schema_json}
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise data analysis assistant. Output only valid JSON matching the requested schema exactly, with no additional text or markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content
            result_json = json.loads(raw_text)
            return ReplacementAnalysisResult(**result_json)
        except json.JSONDecodeError:
            raise ValueError(f"Model failed to generate valid JSON. Raw output: {raw_text}")
        except Exception as e:
            logger.error(f"Groq Replacement Analysis API error: {e}")
            raise

    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:
        return '# Groq Learning Path\n\n(Not yet implemented)'
