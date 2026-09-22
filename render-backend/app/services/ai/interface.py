from abc import ABC, abstractmethod
from typing import Dict, Any
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult, AIResumeInput, AIResumeResult

class AIProvider(ABC):
    @abstractmethod
    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        pass

    @abstractmethod
    async def analyze_graph(self, input_data: AIAnalysisInput) -> AIGraphAnalysisResult:
        pass

    @abstractmethod
    async def analyze_resume(self, input_data: AIResumeInput) -> AIResumeResult:
        pass

    @abstractmethod
    async def analyze_replacement(self, original_resource: dict, task_name: str, existing_resources: list, task_graph: dict, existing_activity: list = None) -> Any:
        pass

        pass
