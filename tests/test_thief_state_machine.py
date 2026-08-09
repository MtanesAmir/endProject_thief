import pytest
from src.core.state_machine import GamePhaseMachine, GamePhase

def test_state_machine():
    fsm = GamePhaseMachine()
    assert fsm.state == GamePhase.WAITING_FOR_OPPONENT
    fsm.transition(GamePhase.COMPUTING_MOVE)
    assert fsm.state == GamePhase.COMPUTING_MOVE
    fsm.transition(GamePhase.COMMITTING)
    assert fsm.state == GamePhase.COMMITTING
    fsm.transition(GamePhase.AWAITING_REVEAL)
    fsm.transition(GamePhase.VERIFYING)
    fsm.transition(GamePhase.WAITING_FOR_OPPONENT)
    with pytest.raises(ValueError):
        fsm.transition(GamePhase.VERIFYING)
