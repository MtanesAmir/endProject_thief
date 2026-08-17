"""Benchmarking utility for multi-round simulation."""
from typing import Dict, Any
from src.core.match_runner import MatchRunner

def run_benchmark(rounds: int = 10) -> Dict[str, Any]:
    runner = MatchRunner()
    thief_wins = 0
    cop_wins = 0
    for _ in range(rounds):
        res = runner.run_simulation()
        outcome = res.get("outcome", res.get("status", ""))
        if "THIEF" in str(outcome).upper():
            thief_wins += 1
        elif "COP" in str(outcome).upper():
            cop_wins += 1
    return {"rounds": rounds, "thief_wins": thief_wins, "cop_wins": cop_wins, "thief_win_rate": thief_wins / max(1, rounds)}

