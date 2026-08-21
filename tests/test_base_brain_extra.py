"""Test base brain abstract methods."""
import pytest
from src.strategy.base_brain import BrainBase

class DummyBrain(BrainBase):
    def _decide_move(self, state):
        return super()._decide_move(state)
        
    def _pick_move(self, state):
        return super()._pick_move(state)

def test_base_brain_abstract_methods():
    """Call abstract methods via super() for coverage."""
    brain = DummyBrain(7)
    with pytest.raises(NotImplementedError):
        brain._decide_move({})
    with pytest.raises(NotImplementedError):
        brain._pick_move({})
