from abc import ABC, abstractmethod
from typing import Dict, Any
from .schemas import AIAnalysisInput, AIAnalysisResult

class AIProvider(ABC):
    @abstractmethod
    async def analyze_task(self, input_data: AIAnalysisInput) -> AIAnalysisResult:
        pass
