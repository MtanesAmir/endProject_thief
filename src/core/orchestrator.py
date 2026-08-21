"""Thief Orchestrator Gateway & turn coordination engine."""
from typing import Any, Dict, List, Optional, Tuple
from src.core.state_machine import GamePhase, GamePhaseMachine
from src.domain.crypto import CommitRevealEngine
from src.domain.scent import ScentTracker
from src.domain.belief import BayesianBeliefGrid
from src.strategy.thief_brain import ThiefBrain
from src.infra.rate_limiter import TokenBucketRateLimiter
from src.domain.barriers import BarrierManager

import time
import logging

logger = logging.getLogger(__name__)

class ThiefOrchestrator:
    def __init__(self, start_pos: Tuple[int, int] = (3, 3), grid_size: int = 7, p2p_server: Optional[Any] = None):
        self.fsm = GamePhaseMachine()
        self.crypto = CommitRevealEngine()
        self.scent_tracker = ScentTracker(grid_size)
        self.belief_grid = BayesianBeliefGrid(grid_size)
        self.brain = ThiefBrain(start_pos=start_pos, grid_size=grid_size)
        self.barriers = BarrierManager(grid_size=grid_size)
        self.rate_limiter = TokenBucketRateLimiter()
        self.step_count = 0
        self.audit_log: List[Dict[str, Any]] = []
        self.p2p_server = p2p_server
        self.current_turn = 0
        self.last_action_data: Optional[Dict[str, Any]] = None

    def handle_incoming_message(self, msg_type: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        
        if msg_type in ("PING", "receive_control"):
            return {"status": "PONG", "timestamp": time.time()}

        if msg_type in ("TURN_INIT", "negotiate"):
            return {"status": "ACK", "turn": self.current_turn, "state": self.fsm.state.name}

        if msg_type in ("PROCESS_TURN", "receive_turn"):
            return self.process_turn(payload)

        if msg_type == "submit_audit":
            # Audit is end-of-game; acknowledge without a FSM transition.
            return {"status": "OK", "msg_type": msg_type, "state": self.fsm.state.name}

        return {"status": "OK", "msg_type": msg_type, "state": self.fsm.state.name}

    def compute_and_commit(self, state: Dict[str, Any]) -> Tuple[str, str, Tuple[int, int]]:
        """Decide a move, generate a bluff, create a SHA-256 commitment.

        Returns:
            (commit_hash, nonce, chosen_position)
        """
        chosen_pos = self.brain._decide_move(
            state, belief_map=self.belief_grid, barriers=self.barriers.get_barriers(),
        )
        hint_text, is_truthful = self.brain._decide_bluff(state, chosen_pos)

        intent_payload = {"message": hint_text, "is_truthful": is_truthful}
        h_commit, nonce = self.crypto.commit(
            state=str(state), move=str(chosen_pos), intent=intent_payload,
        )

        self.audit_log.append({
            "step": self.current_turn + 1,
            "commit": h_commit,
            "move": str(chosen_pos),
            "nonce": nonce,
            "hint": hint_text,
        })
        return h_commit, nonce, chosen_pos

    def record_verified_turn(
        self,
        opponent_move: Tuple[int, int],
        opponent_hint: str,
    ) -> None:
        """Record verified opponent data and update scent / belief grids."""
        self.scent_tracker.update_scent(opponent_move)
        self.belief_grid.update_with_scent(self.scent_tracker.get_matrix())
        self.belief_grid.update_with_hint(opponent_hint)
        self.belief_grid.normalize()
        self.step_count += 1
        self.current_turn += 1

    def process_turn(self, opponent_move_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            # 1. Transition to COMPUTING_MOVE
            self.fsm.transition(GamePhase.COMPUTING_MOVE)

            state = {} # dummy state for now
            chosen_pos = self.brain._decide_move(state, belief_map=self.belief_grid, barriers=self.barriers.get_barriers())
            hint_text, is_truthful = self.brain._decide_bluff(state, chosen_pos)
            
            # 2. Transition to COMMITTING
            self.fsm.transition(GamePhase.COMMITTING)
            
            intent_payload = {
                "message": hint_text,
                "is_truthful": is_truthful
            }
            h_commit, nonce = self.crypto.commit(state=str(state), move=str(chosen_pos), intent=intent_payload)
            self.audit_log.append({"step": self.current_turn + 1, "commit": h_commit, "move": str(chosen_pos), "nonce": nonce, "hint": hint_text})
            
            # 3. Transition to AWAITING_REVEAL
            self.fsm.transition(GamePhase.AWAITING_REVEAL)

            # 4. Transition to VERIFYING
            self.fsm.transition(GamePhase.VERIFYING)

            # 5. Return to WAITING_FOR_OPPONENT
            self.fsm.transition(GamePhase.WAITING_FOR_OPPONENT)
            self.current_turn += 1

            self.last_action_data = {
                "step": self.current_turn,
                "sender": "thief",
                "commit": h_commit,
                "hint": hint_text,
                "timestamp": str(time.time()),
                "smell_grid": {},
                "barrier_placed": None,
                "capture_claim": None,
                "claim_response": None,
                "win_claim": None,
            }

            if self.p2p_server:
                self.p2p_server.call_opponent("receive_turn", self.last_action_data)

            return {
                "success": True,
                "state": self.fsm.state.name,
                "data": self.last_action_data,
            }

        except Exception as e:
            logger.error(f"Error encountered during turn processing: {e}")
            self.fsm.transition(GamePhase.TECHNICAL_LOSS)
            return {
                "success": False,
                "error": str(e),
                "state": self.fsm.state.name,
            }
