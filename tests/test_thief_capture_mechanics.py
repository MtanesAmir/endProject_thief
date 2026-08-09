import pytest
from src.domain.capture import is_captured, evaluate_match_result

def test_capture_detection():
    assert is_captured((3, 3), (3, 3)) is True
    assert is_captured((0, 0), (3, 3)) is False

def test_evaluate_match_result():
    res1 = evaluate_match_result((3, 3), (3, 3), 10, 35)
    assert res1["outcome"] == "COP_CAPTURE"
    assert res1["terminal"] is True

    res2 = evaluate_match_result((0, 0), (3, 3), 35, 35)
    assert res2["outcome"] == "THIEF_SURVIVAL"
    assert res2["terminal"] is True
