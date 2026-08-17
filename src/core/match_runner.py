"""Full match execution loop and round simulation.

Implements a proper step-by-step Dec-POMDP game loop:
    Move → Commit → Reveal → Verify → Check Capture → Update Scent/Belief → Repeat

The Thief operates under partial observability (belief estimation only),
while the local Cop simulator uses scent-based tracking.
"""
import logging
from typing import Dict, Any, List, Tuple

from src.core.orchestrator import ThiefOrchestrator
from src.strategy.police_brain import MyPoliceBrain
from src.domain.capture import evaluate_match_result
from src.domain.scent import ScentTracker
from src.domain.belief import BayesianBeliefGrid
from src.domain.crypto import CommitRevealEngine
from src.shared.constants import (
    THIEF_START_POS, COP_START_POS, MAX_MOVES, GRID_SIZE,
)

logger = logging.getLogger(__name__)


class MatchRunner:
    """Runs a local simulation match between the Thief and a Police agent.

    Both agents operate under partial observability:
    - The Thief uses a Bayesian belief grid updated by cop scent + verbal hints.
    - The Cop uses a scent tracker updated by the thief's movements.
    Neither agent receives the opponent's raw position directly.
    """

    def __init__(self, max_steps: int = MAX_MOVES, grid_size: int = GRID_SIZE):
        self.max_steps = max_steps
        self.grid_size = grid_size

    def run_simulation(self) -> Dict[str, Any]:
        """Execute a full match and return the result dictionary."""

        # ── Initialise agents ──────────────────────────────────────────
        thief_orchestrator = ThiefOrchestrator(
            start_pos=THIEF_START_POS, grid_size=self.grid_size,
        )
        cop_brain = MyPoliceBrain(
            start_pos=COP_START_POS, grid_size=self.grid_size,
        )

        # Cop's own scent tracker and belief grid for the thief
        cop_scent = ScentTracker(self.grid_size)
        cop_belief = BayesianBeliefGrid(self.grid_size)
        cop_crypto = CommitRevealEngine()

        thief_pos: Tuple[int, int] = THIEF_START_POS
        cop_pos: Tuple[int, int] = COP_START_POS

        audit_log: List[Dict[str, Any]] = []

        # ── Game loop ──────────────────────────────────────────────────
        for step in range(self.max_steps):

            # 0. Check pre-move capture (agents on same cell)
            pre_result = evaluate_match_result(cop_pos, thief_pos, step)
            if pre_result["terminal"]:
                return self._build_result(pre_result, step, audit_log)

            # ── 1. Thief decides (partial observability) ───────────────
            thief_state = {
                "step": step,
                "my_position": thief_pos,
                # No cop_position! Thief relies on belief grid.
            }
            t_commit, t_nonce, thief_move = thief_orchestrator.compute_and_commit(thief_state)
            t_hint, t_truthful = thief_orchestrator.brain._decide_bluff(thief_state, thief_move)

            # ── 2. Cop decides (partial observability via scent) ───────
            cop_estimated_thief = cop_belief.get_most_likely_position()
            cop_state = {
                "step": step,
                "my_position": cop_pos,
                "thief_pos": cop_estimated_thief,  # Cop uses its own estimate
            }
            cop_move = cop_brain._decide_move(cop_state)
            c_commit, c_nonce = cop_crypto.commit(
                state=str(cop_state), move=str(cop_move), intent="pursuit",
            )

            # ── 3. Commit exchange (both sides lock) ───────────────────
            #   In real P2P this goes over the network; here it's local.

            # ── 4. Reveal & Verify ─────────────────────────────────────
            thief_verified = cop_crypto.verify(
                t_commit, state=str(thief_state), move=str(thief_move),
                intent={"message": t_hint, "is_truthful": t_truthful},
                nonce=t_nonce,
            )

            # ── 5. Apply moves ─────────────────────────────────────────
            thief_pos = thief_move
            cop_pos = cop_move

            # ── 6. Post-move capture check ─────────────────────────────
            post_result = evaluate_match_result(cop_pos, thief_pos, step + 1)

            # ── 7. Update scent & belief for both agents ───────────────
            # Thief records cop's move and hint (learns about cop)
            cop_hint_to_thief = "I moved north"  # Cop's verbal hint (simplified)
            thief_orchestrator.record_verified_turn(cop_move, cop_hint_to_thief)

            # Cop records thief's scent trail and hint
            cop_scent.update_scent(thief_pos)
            cop_belief.update_with_scent(cop_scent.get_matrix())
            cop_belief.update_with_hint(t_hint)
            cop_belief.normalize()

            # ── 8. Audit log entry ─────────────────────────────────────
            audit_log.append({
                "step": step,
                "thief_pos": list(thief_pos),
                "cop_pos": list(cop_pos),
                "thief_commit": t_commit,
                "cop_commit": c_commit,
                "thief_hint": t_hint,
                "thief_verified": thief_verified,
                "distance": abs(thief_pos[0] - cop_pos[0]) + abs(thief_pos[1] - cop_pos[1]),
            })

            logger.debug(
                "Step %d: Thief=%s Cop=%s dist=%d",
                step, thief_pos, cop_pos, audit_log[-1]["distance"],
            )

            if post_result["terminal"]:
                return self._build_result(post_result, step + 1, audit_log)

        # ── Thief survived all steps ───────────────────────────────────
        final = evaluate_match_result(cop_pos, thief_pos, self.max_steps)
        return self._build_result(final, self.max_steps, audit_log)

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _build_result(
        result: Dict[str, Any],
        steps: int,
        audit_log: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        result["steps"] = steps
        result["audit_log"] = audit_log
        result["total_steps"] = steps
        return result
