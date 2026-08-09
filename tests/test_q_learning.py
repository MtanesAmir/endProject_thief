import pytest
from src.strategy.q_learning import QLearningAgent

def test_q_learning():
    agent = QLearningAgent(alpha=0.1, gamma=0.9, epsilon=0.0)
    act = agent.choose_action("s1", ["UP", "DOWN"])
    assert act in ["UP", "DOWN"]
    agent.update("s1", "UP", 10.0, "s2", ["UP", "DOWN"])
    assert agent.q_table[("s1", "UP")] > 0.0
    empty_act = agent.choose_action("s1", [])
    assert empty_act == "STAY"
