"""LLM provider abstraction supporting template, Ollama, and OpenAI backends."""
import os
import json
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LLMProvider:
    """Multi-backend LLM provider for bluff generation.

    Supported providers:
        - "template": Zero-cost canned responses (default, no API needed).
        - "ollama":   Local Ollama server at http://localhost:11434.
        - "openai":   OpenAI-compatible API using OPENAI_API_KEY env var.
    """

    def __init__(self, provider_type: str = "template"):
        self.provider_type = provider_type
        self.total_tokens = 0

    def generate_bluff(self, context: Dict[str, Any], actual_move: str, word_limit: int = 15) -> str:
        if self.provider_type == "ollama":
            return self._generate_ollama(context, actual_move, word_limit)
        elif self.provider_type == "openai":
            return self._generate_openai(context, actual_move, word_limit)
        else:
            return self._generate_template(context, actual_move, word_limit)

    def _build_prompt(self, context: Dict[str, Any], actual_move: str, word_limit: int) -> str:
        return (
            f"You are a highly evasive Thief in a grid-based pursuit game. "
            f"Your actual planned move is: {actual_move}. "
            f"Game State: {context}. "
            f"Generate a deceptive hint to mislead the Cop that contradicts your actual move. "
            f"Limit your response to exactly {word_limit} words or fewer. "
            f"Respond ONLY with the deceptive hint text, nothing else."
        )

    def _generate_template(self, context: Dict[str, Any], actual_move: str, word_limit: int) -> str:
        self.total_tokens += 15  # dummy tracking
        return f"I moved {actual_move} towards the shadows."

    def _generate_ollama(self, context: Dict[str, Any], actual_move: str, word_limit: int) -> str:
        """Generate bluff via local Ollama server (http://localhost:11434)."""

        model = os.environ.get("OLLAMA_MODEL", "llama3.2")
        prompt = self._build_prompt(context, actual_move, word_limit)

        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "").strip()
            # Track tokens from Ollama response metadata
            self.total_tokens += data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
            return text if text else self._generate_template(context, actual_move, word_limit)
        except Exception as e:
            logger.warning("Ollama generation failed, falling back to template: %s", e)
            return self._generate_template(context, actual_move, word_limit)

    def _generate_openai(self, context: Dict[str, Any], actual_move: str, word_limit: int) -> str:
        """Generate bluff via OpenAI-compatible API (requires OPENAI_API_KEY)."""

        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

        if not api_key:
            logger.warning("OPENAI_API_KEY not set, falling back to template.")
            return self._generate_template(context, actual_move, word_limit)

        prompt = self._build_prompt(context, actual_move, word_limit)

        try:
            resp = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": word_limit * 3,
                    "temperature": 0.9,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            # Track OpenAI token usage
            usage = data.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            return text if text else self._generate_template(context, actual_move, word_limit)
        except Exception as e:
            logger.warning("OpenAI generation failed, falling back to template: %s", e)
            return self._generate_template(context, actual_move, word_limit)
