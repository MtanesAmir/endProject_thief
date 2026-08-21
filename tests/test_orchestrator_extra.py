"""Tests for orchestrator exception handling."""
import pytest
from src.core.orchestrator import ThiefOrchestrator
from src.core.state_machine import GamePhase

def test_orchestrator_process_turn_exception():
    """Test process_turn catches exceptions and transitions to TECHNICAL_LOSS."""
    orch = ThiefOrchestrator((3, 3), 7)
    
    # Mock the brain to throw an exception during process_turn
    def mock_decide_move(*args, **kwargs):
        raise RuntimeError("Simulated failure")
        
    orch.brain._decide_move = mock_decide_move
    
    result = orch.process_turn({})
    
    assert result["success"] is False
    assert "error" in result
    assert result["state"] == "TECHNICAL_LOSS"
    assert orch.fsm.state == GamePhase.TECHNICAL_LOSS
