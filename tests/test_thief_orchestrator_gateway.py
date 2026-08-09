import pytest
from src.core.orchestrator import ThiefOrchestrator

def test_orchestrator():
    orch = ThiefOrchestrator((3, 3), 7)
    h, nonce, pos = orch.compute_and_commit({"cop_position": (0, 0)})
    assert len(h) == 64
    assert len(nonce) == 32
    orch.record_verified_turn((1, 0), "cop_hint")
    assert orch.step_count == 1
