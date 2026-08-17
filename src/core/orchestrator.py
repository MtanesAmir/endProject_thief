"""Thief Orchestrator Gateway & turn coordination engine."""
from typing import Any, Dict, List, Optional, Tuple
from src.core.state_machine import GamePhase, GamePhaseMachine
from src.domain.crypto import CommitRevealEngine
from src.domain.scent import ScentTracker
from src.domain.belief import BayesianBeliefGrid
from src.strategy.thief_brain import ThiefBrain
from src.infra.rate_limiter import TokenBucketRateLimiter
from src.domain.barriers import BarrierManager

class ThiefOrchestrator:
    def __init__(self, start_pos: Tuple[int, int] = (3, 3), grid_size: int = 7):
        self.fsm = GamePhaseMachine()
        self.crypto = CommitRevealEngine()
        self.scent_tracker = ScentTracker(grid_size)
        self.belief_grid = BayesianBeliefGrid(grid_size)
        self.brain = ThiefBrain(start_pos=start_pos, grid_size=grid_size)
        self.barriers = BarrierManager(grid_size=grid_size)
        self.rate_limiter = TokenBucketRateLimiter()
        self.step_count = 0
        self.audit_log: List[Dict[str, Any]] = []

    def compute_and_commit(self, state: Dict[str, Any]) -> Tuple[str, str, Tuple[int, int]]:
        self.fsm.transition(GamePhase.COMPUTING_MOVE)
        chosen_pos = self.brain._decide_move(state, belief_map=self.belief_grid, barriers=self.barriers.get_barriers())
        hint_text, is_truthful = self.brain._decide_bluff(state, chosen_pos)
        self.fsm.transition(GamePhase.COMMITTING)
        
        intent_payload = {
            "message": hint_text,
            "is_truthful": is_truthful
        }
        
        h_commit, nonce = self.crypto.commit(state=str(state), move=str(chosen_pos), intent=intent_payload)
        self.audit_log.append({"step": self.step_count, "commit": h_commit, "move": str(chosen_pos), "nonce": nonce, "hint": hint_text})
        return h_commit, nonce, chosen_pos

    def record_verified_turn(self, peer_move: Any, peer_hint: str) -> None:
        self.fsm.transition(GamePhase.AWAITING_REVEAL)
        self.fsm.transition(GamePhase.VERIFYING)
        if isinstance(peer_move, tuple) and len(peer_move) == 2:
            self.scent_tracker.update_scent(peer_move)
        elif isinstance(peer_move, list) and len(peer_move) == 2:
            self.scent_tracker.update_scent(tuple(peer_move))
        
        scent = self.scent_tracker.get_matrix()
        self.belief_grid.update_with_scent(scent)
        self.belief_grid.update_with_hint(peer_hint)
        self.belief_grid.normalize()
        
        self.step_count += 1
        self.fsm.transition(GamePhase.WAITING_FOR_OPPONENT)
