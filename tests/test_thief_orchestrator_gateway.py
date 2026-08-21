"""Comprehensive tests for ThiefOrchestrator process_turn and message handling."""
import pytest
from src.core.orchestrator import ThiefOrchestrator
from src.core.state_machine import GamePhase


def test_orchestrator_compute_and_commit():
    """Test compute_and_commit returns valid hash, nonce, and position."""
    orch = ThiefOrchestrator((3, 3), 7)
    h, nonce, pos = orch.compute_and_commit({"cop_position": (0, 0)})
    assert len(h) == 64
    assert len(nonce) == 32
    assert isinstance(pos, tuple)
    assert len(pos) == 2
    assert 0 <= pos[0] < 7
    assert 0 <= pos[1] < 7


def test_orchestrator_record_verified_turn():
    """Test record_verified_turn updates scent, belief, and counters."""
    orch = ThiefOrchestrator((3, 3), 7)
    assert orch.step_count == 0
    assert orch.current_turn == 0

    orch.record_verified_turn((1, 0), "I moved north")
    assert orch.step_count == 1
    assert orch.current_turn == 1

    # Belief grid should have been updated (no longer uniform)
    grid = orch.belief_grid.get_grid()
    # After scent update at (1,0), that area should have higher probability
    assert isinstance(grid, list)
    assert len(grid) == 7


def test_orchestrator_process_turn():
    """Test the full process_turn FSM cycle."""
    orch = ThiefOrchestrator((3, 3), 7)
    assert orch.fsm.state == GamePhase.WAITING_FOR_OPPONENT

    result = orch.process_turn({})
    assert result["success"] is True
    assert result["state"] == "WAITING_FOR_OPPONENT"
    assert "data" in result
    assert result["data"]["sender"] == "thief"
    assert len(result["data"]["commit"]) == 64
    assert orch.current_turn == 1
    assert orch.last_action_data is not None


def test_orchestrator_process_turn_multiple():
    """Test multiple consecutive turns through process_turn."""
    orch = ThiefOrchestrator((3, 3), 7)
    for i in range(3):
        result = orch.process_turn({})
        assert result["success"] is True
        assert orch.current_turn == i + 1


def test_orchestrator_handle_ping():
    """Test PING message handling."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("PING")
    assert result["status"] == "PONG"
    assert "timestamp" in result


def test_orchestrator_handle_receive_control():
    """Test receive_control message handling."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("receive_control", {"command": "status"})
    assert result["status"] == "PONG"


def test_orchestrator_handle_negotiate():
    """Test negotiate message handling."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("negotiate", {"terms": {}})
    assert result["status"] == "ACK"
    assert "turn" in result
    assert "state" in result


def test_orchestrator_handle_turn_init():
    """Test TURN_INIT message handling."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("TURN_INIT", {})
    assert result["status"] == "ACK"


def test_orchestrator_handle_receive_turn():
    """Test receive_turn message triggers process_turn."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("receive_turn", {})
    assert result["success"] is True


def test_orchestrator_handle_process_turn():
    """Test PROCESS_TURN message triggers process_turn."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("PROCESS_TURN", {})
    assert result["success"] is True
    assert result["data"]["sender"] == "thief"


def test_orchestrator_handle_submit_audit():
    """Test submit_audit message handling (end-of-game)."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("submit_audit", {"records": []})
    assert result["status"] == "OK"
    assert result["msg_type"] == "submit_audit"


def test_orchestrator_handle_unknown_message():
    """Test unknown message type returns OK."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("UNKNOWN_MSG_TYPE", {})
    assert result["status"] == "OK"
    assert result["msg_type"] == "UNKNOWN_MSG_TYPE"


def test_orchestrator_handle_none_payload():
    """Test message handler with None payload."""
    orch = ThiefOrchestrator()
    result = orch.handle_incoming_message("PING", None)
    assert result["status"] == "PONG"


def test_orchestrator_audit_log_populated():
    """Test that audit_log is populated after process_turn."""
    orch = ThiefOrchestrator()
    orch.process_turn({})
    assert len(orch.audit_log) == 1
    entry = orch.audit_log[0]
    assert "step" in entry
    assert "commit" in entry
    assert "move" in entry
    assert "nonce" in entry
    assert "hint" in entry


def test_orchestrator_with_p2p_server():
    """Test process_turn with a mock P2P server."""
    calls = []

    class MockP2P:
        def call_opponent(self, method, data):
            calls.append((method, data))
            return {"status": "enqueued"}

    mock = MockP2P()
    orch = ThiefOrchestrator(p2p_server=mock)
    result = orch.process_turn({})
    assert result["success"] is True
    assert len(calls) == 1
    assert calls[0][0] == "receive_turn"
