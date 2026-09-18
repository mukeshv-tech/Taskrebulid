from app.services.ai.interface import AIProvider

class PlaceholderAI(AIProvider):
    def process(self, input_text: str) -> str:
        return f"Processed: {input_text} (AI is disabled)"
