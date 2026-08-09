"""LLM provider abstraction for template, local Ollama, or API calls."""
from typing import Dict, Any

class LLMProvider:
    def __init__(self, provider_type: str = "template"):
        self.provider_type = provider_type

    def generate_bluff(self, context: Dict[str, Any]) -> str:
        if self.provider_type == "template":
            return "I moved west towards the abandoned warehouse."
        return "I am changing positions."
