"""Bluff classifier and deceptive hint generator."""
import random
from typing import List, Tuple

class BluffGenerator:
    def __init__(self):
        self.directions = ["N", "S", "E", "W"]

    def generate_deceptive_hint(self, actual_move: str) -> str:
        options = [d for d in self.directions if d != actual_move]
        chosen = random.choice(options) if options else "STAY"
        return f"I moved {chosen}"

    def generate_truthful_hint(self, actual_move: str) -> str:
        return f"I moved {actual_move}"

    def classify_hint_reliability(self, hint: str, observed_scent: float) -> float:
        return 0.5 if observed_scent < 0.2 else 0.85
