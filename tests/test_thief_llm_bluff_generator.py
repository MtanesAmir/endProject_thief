import pytest
from unittest.mock import patch, MagicMock
from src.infra.llm_provider import LLMProvider


# Helper to check if a string contains a valid deceptive direction hint
def _has_direction(text):
    return any(d in text.lower() for d in ["north", "south", "east", "west"])


def test_template_provider():
    p = LLMProvider("template")
    result = p.generate_bluff(context={"step": 1}, actual_move="(3, 3)")
    assert _has_direction(result)
    assert p.total_tokens == 15


def test_ollama_fallback_on_error():
    """Ollama provider should fall back to template when request fails."""
    p = LLMProvider("ollama")
    with patch("src.infra.llm_provider.requests") as mock_req:
        mock_req.post.side_effect = Exception("Connection refused")
        result = p.generate_bluff(context={}, actual_move="(2, 2)")
    assert _has_direction(result)  # Fell back to template


def test_openai_fallback_no_key():
    """OpenAI provider should fall back to template when no API key is set."""
    p = LLMProvider("openai")
    with patch.dict("os.environ", {}, clear=True):
        result = p.generate_bluff(context={}, actual_move="(1, 1)")
    assert _has_direction(result)  # Fell back to template


def test_openai_fallback_on_error():
    """OpenAI provider should fall back to template when request fails."""
    p = LLMProvider("openai")
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("src.infra.llm_provider.requests") as mock_req:
            mock_req.post.side_effect = Exception("API error")
            result = p.generate_bluff(context={}, actual_move="(4, 4)")
    assert _has_direction(result)  # Fell back to template


def test_ollama_success():
    """Ollama provider should return LLM response on success."""
    p = LLMProvider("ollama")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "I am heading west towards the river",
        "eval_count": 10,
        "prompt_eval_count": 20,
    }
    mock_response.raise_for_status = MagicMock()

    with patch("src.infra.llm_provider.requests") as mock_req:
        mock_req.post.return_value = mock_response
        result = p.generate_bluff(context={}, actual_move="(3, 3)")

    assert "west" in result or "river" in result
    assert p.total_tokens == 30


def test_openai_success():
    """OpenAI provider should return LLM response on success."""
    p = LLMProvider("openai")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Moving toward the east exit"}}],
        "usage": {"total_tokens": 42},
    }
    mock_response.raise_for_status = MagicMock()

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("src.infra.llm_provider.requests") as mock_req:
            mock_req.post.return_value = mock_response
            result = p.generate_bluff(context={}, actual_move="(2, 2)")

    assert "east" in result
    assert p.total_tokens == 42


def test_build_prompt():
    p = LLMProvider("template")
    prompt = p._build_prompt(context={"step": 5}, actual_move="(3, 3)", word_limit=15)
    assert "deceptive" in prompt.lower()
    assert "(3, 3)" in prompt


def test_template_does_not_leak_position():
    """Critical test: ensure the template does NOT include the actual move coordinates."""
    p = LLMProvider("template")
    result = p.generate_bluff(context={}, actual_move="(5, 2)")
    # The actual coordinates must NOT appear in the hint
    assert "(5, 2)" not in result
    assert "5, 2" not in result
