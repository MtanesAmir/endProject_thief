"""LLM provider abstraction for template, local Ollama, or API calls."""
from typing import Dict, Any

class LLMProvider:
    def __init__(self, provider_type: str = "template"):
        self.provider_type = provider_type
        self.total_tokens = 0

    def generate_bluff(self, context: Dict[str, Any], actual_move: str, word_limit: int = 15) -> str:
        if self.provider_type == "template":
            self.total_tokens += 15 # dummy tracking
            return f"I moved {actual_move} towards the shadows."
            
        prompt = f"""
        You are a highly evasive Thief in a grid-based pursuit game.
        Your actual planned move is: {actual_move}.
        Game State: {context}
        Generate a deceptive hint to mislead the Cop that contradicts your actual move. 
        Limit your response to exactly {word_limit} words or fewer.
        """
        # Execute LLM generation logic here...
        self.total_tokens += 60 # dummy tracking
        return "I am changing positions."
