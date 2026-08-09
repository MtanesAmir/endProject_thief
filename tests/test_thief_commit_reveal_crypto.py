import pytest
from src.domain.crypto import CommitmentScheme, CommitRevealEngine

def test_commitment_scheme():
    scheme = CommitmentScheme()
    h, nonce = scheme.create_commitment("N")
    assert scheme.verify_reveal(h, "N", nonce) is True
    assert scheme.verify_reveal(h, "S", nonce) is False

def test_commit_reveal_engine():
    engine = CommitRevealEngine()
    h, nonce = engine.commit(state="s1", move="MOVE_UP", intent="truth")
    assert engine.verify(h, state="s1", move="MOVE_UP", intent="truth", nonce=nonce) is True
    assert engine.verify(h, state="s2", move="MOVE_UP", intent="truth", nonce=nonce) is False
