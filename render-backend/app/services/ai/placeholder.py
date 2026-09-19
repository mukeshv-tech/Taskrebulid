from .interface import AIProvider
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult

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
