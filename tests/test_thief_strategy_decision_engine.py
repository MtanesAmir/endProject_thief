import pytest
from src.strategy.thief_brain import ThiefBrain

def test_thief_brain():
    tb = ThiefBrain((3, 3), 7)
    move = tb._decide_move({"cop_position": (3, 2)})
    assert move != (3, 2)
    bluff_text, is_truthful = tb._decide_bluff({}, move)
    assert "I moved" in bluff_text
    assert isinstance(is_truthful, bool)
