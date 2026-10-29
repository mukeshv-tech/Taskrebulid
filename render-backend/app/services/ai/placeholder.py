from typing import Dict, Any, List
from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult, AIResumeInput, AIResumeResult

class PlaceholderAIProvider(AIProvider):
    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:
        return '# Placeholder Learning Path'

    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        return AIAnalysisResult(
            task_summary="Placeholder AI: Task analysis not available.",
            topics=[],
            resource_analysis=[],
            activity_summary="Placeholder AI: Activity analysis not available.",
            suggested_next_steps=[]
        )

    async def analyze_graph(self, input_data: AIAnalysisInput) -> AIGraphAnalysisResult:
        return AIGraphAnalysisResult(
            nodes=[],
            edges=[]
        )

    async def analyze_resume(self, input_data: AIResumeInput) -> AIResumeResult:
        return AIResumeResult(
            resume_summary="Placeholder AI: Resume analysis not available.",
            what_you_were_doing="Placeholder AI...",
            last_known_progress="Placeholder AI...",
            important_resources=[],
            open_questions=[],
            next_steps=[]
        )

    async def analyze_replacement(self, original_resource: dict, task_name: str, existing_resources: list, task_graph: dict, existing_activity: list = None):
        from .schemas import ReplacementAnalysisResult, ReplacementCandidate
        return ReplacementAnalysisResult(
            original_resource_id=original_resource.get('id', 'unknown'),
            candidates=[
                ReplacementCandidate(
                    resource_id=existing_resources[0]['id'] if existing_resources else 'none',
                    reason="Placeholder suggestion",
                    confidence=0.8
                )
            ]
        )

    async def suggest_knowledge(self, task_data: Dict[str, Any], existing_knowledge: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        task_name = task_data.get("name", "Task")
        return {
            "suggestions": [
                {
                    "type": "concept",
                    "title": f"Key concept in {task_name}",
                    "summary": f"Foundational understanding extracted from {task_name}.",
                    "content": f"Detailed notes on {task_name} for future reuse across different tasks.",
                    "confidence": 0.8,
                    "source_name": task_name,
                    "source_type": "task",
                    "source_id": task_data.get("id")
                }
            ],
            "suggested_relationships": []
        }
