import pytest
from src.p2p.server import create_p2p_server
from src.domain.crypto import CommitRevealEngine
import json


def test_p2p_server_creation():
    server = create_p2p_server(name="thief", port=8802)
    assert server is not None
    assert server.name == "thief"
    assert server.port == 8802
    assert hasattr(server, "crypto_engine")


def test_p2p_hash_consistency():
    """Verify P2P server uses the same canonical JSON hashing as the crypto engine."""
    engine = CommitRevealEngine()
    state = "test_state"
    move = "(3, 3)"
    intent = {"message": "I moved north", "is_truthful": False}
    h_commit, nonce = engine.commit(state=state, move=move, intent=intent)

    # The engine should verify its own commitment
    assert engine.verify(h_commit, state=state, move=move, intent=intent, nonce=nonce)

    # Tampered move should fail
    assert not engine.verify(h_commit, state=state, move="(4, 4)", intent=intent, nonce=nonce)


def test_p2p_receive_commit_and_verify():
    """Test the full commit-reveal flow through the P2P server's crypto engine."""
    server = create_p2p_server(name="test_peer", port=9999)
    engine = server.crypto_engine

    state = "game_state_1"
    move = "(2, 3)"
    intent = {"message": "heading south", "is_truthful": False}

    # Commit
    h_commit, nonce = engine.commit(state=state, move=move, intent=intent)
    server.stored_commit = h_commit

    # Verify valid reveal
    assert engine.verify(h_commit, state=state, move=move, intent=intent, nonce=nonce)

    # Verify tampered reveal fails
    assert not engine.verify(h_commit, state=state, move="(5, 5)", intent=intent, nonce=nonce)

    # Reset
    server.stored_commit = None
    assert server.stored_commit is None
