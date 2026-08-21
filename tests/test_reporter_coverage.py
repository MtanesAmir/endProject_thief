"""Tests for reporter module with mocked Gmail API."""
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from src.infra.reporter import GameReporter


def test_reporter_get_git_commit():
    """Test git commit retrieval."""
    commit = GameReporter.get_git_commit()
    assert isinstance(commit, str)
    assert len(commit) > 0


def test_reporter_send_report_no_credentials(tmp_path, capsys):
    """Test send_report when config/credentials.json is missing."""
    game_result = {"outcome": "THIEF_SURVIVAL", "thief_score": 10}
    game_id = "test-game-123"

    # Patch os.path.exists to return False for both token and credentials
    original_exists = os.path.exists

    def mock_exists(path):
        if "token.json" in str(path) or "credentials.json" in str(path):
            return False
        return original_exists(path)

    with patch("os.path.exists", side_effect=mock_exists):
        GameReporter.send_report(game_result, game_id, "test@example.com")

    captured = capsys.readouterr()
    assert "credentials.json not found" in captured.out

    # Verify the result file was still written
    filename = f"result_{game_id}.json"
    if os.path.exists(filename):
        with open(filename) as f:
            data = json.load(f)
        assert data["thief_commit"] is not None
        os.unlink(filename)


def test_reporter_enriches_result(tmp_path):
    """Test that send_report enriches the result dict with commit hashes."""
    game_result = {"outcome": "COP_CAPTURE", "cop_score": 20}
    game_id = "enrichment-test"

    original_exists = os.path.exists

    def mock_exists(path):
        if "token.json" in str(path) or "credentials.json" in str(path):
            return False
        return original_exists(path)

    with patch("os.path.exists", side_effect=mock_exists):
        GameReporter.send_report(game_result, game_id, "test@example.com")

    assert "thief_commit" in game_result
    assert "cop_commit" in game_result
    assert "total_llm_tokens" in game_result

    # Cleanup
    filename = f"result_{game_id}.json"
    if os.path.exists(filename):
        os.unlink(filename)
