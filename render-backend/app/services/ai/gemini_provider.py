import json
import logging
import google.generativeai as genai
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult, AIResumeInput, AIResumeResult

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str):
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

    async def analyze_graph(self, input_data: AIAnalysisInput) -> AIGraphAnalysisResult:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

        # Prepare the prompt
        prompt = f"""
You are an AI assistant analyzing a user's research task to extract a knowledge graph.
Task Name: {input_data.task_name}

Resources:
{json.dumps([r.model_dump() for r in input_data.resources], indent=2)}

Recent Activity:
{json.dumps([a.model_dump() for a in input_data.activity], indent=2)}

INSTRUCTIONS:
Extract a COMPREHENSIVE and EXHAUSTIVE structured knowledge graph (nodes and edges) representing ALL entities, concepts, and relationships found in the provided Resources and Activity.
1. DO NOT summarize or skip activities. Create nodes for every distinct topic, tool, document, or website visited in the activity log.
2. Use only supplied information. Do not invent resources, facts, or URLs.
3. Deduplicate nodes. E.g., "Machine Learning" and "machine learning" should be a single node. Don't aggressively merge concepts if uncertain.
4. Node labels must be clear and concise.
5. Edge relationship types must be one of: "related_to", "about", "requires", "answers", "part_of", "references".
6. Provide evidence for edges strictly referring to the provided resource IDs or activity context. Return no relationship when evidence is insufficient.
7. Confidence must be between 0.0 and 1.0 based on the evidence strength.

Output JSON matching this exact structure:
{{
  "nodes": [
    {{ "label": "String", "node_type": "topic|concept|question|goal|resource", "description": "String", "confidence": 0.95 }}
  ],
  "edges": [
    {{ "source_label": "String", "target_label": "String", "relationship_type": "related_to", "confidence": 0.85, "evidence": [ {{ "resource_id": "String or null", "reason": "String" }} ] }}
  ]
}}
Respond strictly in valid JSON without markdown wrapping.
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
            
            return AIGraphAnalysisResult(**result_json)
        except Exception as e:
            logger.error(f"Gemini Graph API error: {e}")
            raise

    async def analyze_resume(self, input_data: AIResumeInput) -> AIResumeResult:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

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
Respond strictly in valid JSON without markdown wrapping.
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
            logger.error("RAW GEMINI GRAPH OUTPUT: " + result_text)
            result_json = json.loads(result_text)
            
            return AIResumeResult(**result_json)
        except Exception as e:
            logger.error(f"Gemini Resume API error: {e}")
            raise

    async def analyze_replacement(self, original_resource: dict, task_name: str, existing_resources: list, task_graph: dict):
        raise NotImplementedError("Gemini does not support analyze_replacement yet")
