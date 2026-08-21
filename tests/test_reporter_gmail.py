"""Tests for the Gmail API delivery in reporter."""
import pytest
import os
from unittest.mock import patch, MagicMock
from src.infra.reporter import GameReporter

def test_reporter_gmail_api_delivery(tmp_path):
    """Test full Gmail delivery flow with mocked Google API."""
    game_result = {"outcome": "THIEF_WIN", "thief_score": 10}
    game_id = "test-gmail-flow"
    
    # Create fake credentials.json to trigger the flow
    cred_file = tmp_path / "credentials.json"
    cred_file.write_text("{}")
    
    mock_flow_instance = MagicMock()
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_flow_instance.run_local_server.return_value = mock_creds
    
    mock_service = MagicMock()
    mock_service.users().messages().send().execute.return_value = {"id": "msg_123"}

    original_exists = os.path.exists
    def mock_exists(path):
        if "credentials.json" in str(path):
            return True
        if "token.json" in str(path):
            return False
        return original_exists(path)

    with patch("os.path.exists", side_effect=mock_exists), \
         patch("src.infra.reporter.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow_instance), \
         patch("src.infra.reporter.build", return_value=mock_service), \
         patch("builtins.open", MagicMock()):
         
        GameReporter.send_report(game_result, game_id, "test@example.com")
        
    mock_service.users().messages().send.assert_called_once()
    
def test_reporter_git_commit_exception():
    """Test git commit fallback on exception."""
    with patch("subprocess.check_output", side_effect=Exception("git error")):
        commit = GameReporter.get_git_commit()
        assert commit == "unknown_commit"
