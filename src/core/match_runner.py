"""Full match execution loop and round simulation."""
from typing import Dict, Any
from src.core.orchestrator import ThiefOrchestrator
from src.domain.capture import evaluate_match_result
from src.strategy.police_brain import MyPoliceBrain

class MatchRunner:
    def __init__(self, max_steps: int = 35):
        self.max_steps = max_steps
        self.thief_orch = ThiefOrchestrator((3, 3), 7)
        self.cop_brain = MyPoliceBrain((0, 0), 7)

    def run_simulation(self) -> Dict[str, Any]:
        cop_pos = (0, 0)
        thief_pos = (3, 3)
        for step in range(1, self.max_steps + 1):
            t_state = {"cop_position": cop_pos, "step": step}
            _, _, thief_pos = self.thief_orch.compute_and_commit(t_state)
            c_state = {"thief_pos": thief_pos, "step": step}
            cop_pos = self.cop_brain._decide_move(c_state)
            self.thief_orch.record_verified_turn(cop_pos, "cop_move")
            res = evaluate_match_result(cop_pos, thief_pos, step, self.max_steps)
            if res["terminal"]:
                return {"steps": step, "outcome": res["outcome"], "cop_score": res["cop_score"], "thief_score": res["thief_score"]}
        res = evaluate_match_result(cop_pos, thief_pos, self.max_steps, self.max_steps)
        return {"steps": self.max_steps, "outcome": res["outcome"], "cop_score": res["cop_score"], "thief_score": res["thief_score"]}
