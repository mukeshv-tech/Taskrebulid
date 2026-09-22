from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult, AIResumeInput, AIResumeResult

class PlaceholderAIProvider(AIProvider):
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
