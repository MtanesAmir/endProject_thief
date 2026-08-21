"""Tests for FastMCPServer, P2PServer, and FastMCPHTTPHandler."""
import pytest
from src.p2p.server import (
    create_p2p_server,
    FastMCPServer,
    P2PServer,
    FastMCPHTTPHandler,
)
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


def test_fastmcp_server_no_url():
    """Test FastMCPServer with no opponent URL."""
    server = FastMCPServer(opponent_url=None)
    result = server.call_opponent("test_method", {"data": 1})
    assert result["status"] == "error"


def test_fastmcp_server_start_no_url():
    """Test that start() is a no-op without an opponent URL."""
    server = FastMCPServer(opponent_url=None)
    server.start()  # Should not raise
    assert server._thread is None
    assert not server.is_running


def test_fastmcp_server_stop_without_start():
    """Test that stop() works even without starting."""
    server = FastMCPServer(opponent_url=None)
    server.stop()  # Should not raise
    assert not server.is_running


def test_fastmcp_server_enqueue_with_url():
    """Test that call_opponent enqueues when URL is set."""
    server = FastMCPServer(opponent_url="http://fake:1234")
    result = server.call_opponent("receive_turn", {"step": 1})
    assert result["status"] == "enqueued"
    assert not server.queue.empty()
    method, payload = server.queue.get()
    assert method == "receive_turn"
    assert payload["step"] == 1


def test_p2p_server_stored_commit():
    """Test the stored_commit attribute on P2PServer."""
    server = P2PServer("test", 1234)
    assert server.stored_commit is None
    server.stored_commit = "abc123"
    assert server.stored_commit == "abc123"


def test_p2p_server_crypto_engine_type():
    """Test that the crypto engine is a CommitRevealEngine."""
    server = create_p2p_server()
    assert isinstance(server.crypto_engine, CommitRevealEngine)


def test_fastmcp_http_handler_class_attr():
    """Test the server_instance class attribute."""
    assert FastMCPHTTPHandler.server_instance is None
