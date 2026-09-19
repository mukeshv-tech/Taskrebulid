from abc import ABC, abstractmethod
from typing import Dict, Any
from .schemas import AIAnalysisInput, AIAnalysisResult, AIGraphAnalysisResult

class AIProvider(ABC):
    @abstractmethod
    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        pass

    @abstractmethod
    async def analyze_graph(self, input_data: AIAnalysisInput) -> AIGraphAnalysisResult:
        pass
