"""Q-learning agent for reinforcement learning pathfinding."""
import random
from typing import Dict, List, Tuple

class QLearningAgent:
    def __init__(self, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table: Dict[Tuple[str, str], float] = {}

    def choose_action(self, state_key: str, legal_actions: List[str]) -> str:
        if not legal_actions:
            return "STAY"
        if random.random() < self.epsilon:
            return random.choice(legal_actions)
        best_a = legal_actions[0]
        max_q = -float("inf")
        for a in legal_actions:
            q = self.q_table.get((state_key, a), 0.0)
            if q > max_q:
                max_q = q
                best_a = a
        return best_a

    def update(self, s: str, a: str, r: float, s_next: str, next_actions: List[str]) -> None:
        max_next = max([self.q_table.get((s_next, na), 0.0) for na in next_actions], default=0.0)
        old_q = self.q_table.get((s, a), 0.0)
        self.q_table[(s, a)] = old_q + self.alpha * (r + self.gamma * max_next - old_q)
