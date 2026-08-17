import pytest
from src.shared.version import get_version_info
from src.shared.constants import GRID_SIZE
from src.infra.llm_provider import LLMProvider
from src.domain.capture import evaluate_match_result

def test_version_info():
    info = get_version_info()
    assert "app_version" in info
    assert info["protocol_version"] == "3.0.0"

def test_llm_provider():
    p1 = LLMProvider("template")
    result = p1.generate_bluff(context={}, actual_move="(3, 3)")
    assert "I moved" in result
    p2 = LLMProvider("custom")
    result2 = p2.generate_bluff(context={}, actual_move="(2, 2)")
    assert isinstance(result2, str)

def test_capture_disqualifications():
    res1 = evaluate_match_result((0, 0), (3, 3), 1, 35, disqualified_role="police")
    assert "THIEF_WIN" in res1["outcome"]
    res2 = evaluate_match_result((0, 0), (3, 3), 1, 35, disqualified_role="thief")
    assert "COP_WIN" in res2["outcome"]
