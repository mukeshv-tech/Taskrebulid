from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def process(self, input_text: str) -> str:
        pass
