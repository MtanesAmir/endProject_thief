"""Finite State Machine for turn lifecycle orchestration."""
from enum import Enum, auto

class GamePhase(Enum):
    WAITING_FOR_OPPONENT = auto()
    COMPUTING_MOVE = auto()
    COMMITTING = auto()
    AWAITING_REVEAL = auto()
    VERIFYING = auto()
    TECHNICAL_LOSS = auto()

TRANSITIONS = {
    GamePhase.WAITING_FOR_OPPONENT: {GamePhase.COMPUTING_MOVE, GamePhase.TECHNICAL_LOSS},
    GamePhase.COMPUTING_MOVE: {GamePhase.COMMITTING, GamePhase.TECHNICAL_LOSS},
    GamePhase.COMMITTING: {GamePhase.AWAITING_REVEAL},
    GamePhase.AWAITING_REVEAL: {GamePhase.VERIFYING, GamePhase.TECHNICAL_LOSS},
    GamePhase.VERIFYING: {GamePhase.WAITING_FOR_OPPONENT},
    GamePhase.TECHNICAL_LOSS: set(),
}

class GamePhaseMachine:
    def __init__(self):
        self.state = GamePhase.WAITING_FOR_OPPONENT

    def transition(self, target: GamePhase) -> GamePhase:
        if target not in TRANSITIONS[self.state]:
            raise ValueError(f"Illegal transition: {self.state} -> {target}")
        self.state = target
        return self.state
