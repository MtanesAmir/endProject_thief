import pytest
from src.domain.bluff import BluffGenerator

def test_bluff_generator():
    bg = BluffGenerator()
    hint = bg.generate_deceptive_hint("N")
    assert "I moved" in hint
    truth = bg.generate_truthful_hint("N")
    assert truth == "I moved N"
    rel = bg.classify_hint_reliability(hint, 0.5)
    assert rel > 0.5
