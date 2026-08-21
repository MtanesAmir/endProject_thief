"""Test LLM provider exception handling."""
import pytest
from src.infra.llm_provider import LLMProvider

def test_template_provider_bad_move():
    """Test the template provider handles malformed actual_move strings."""
    p = LLMProvider("template")
    # This should trigger ValueError or IndexError and fallback to random direction
    result = p.generate_bluff(context={"step": 1}, actual_move="invalid_tuple")
    assert any(d in result.lower() for d in ["north", "south", "east", "west"])
