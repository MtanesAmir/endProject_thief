"""Additional CLI tests for full coverage."""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from src.cli import main

def test_cli_match_with_report(capsys):
    """Test the match command with reporting enabled."""
    mock_reporter = MagicMock()
    with patch.dict("sys.modules", {"src.infra.reporter": MagicMock(GameReporter=mock_reporter)}):
        with patch.object(sys, "argv", ["src.cli", "match", "--rounds", "1", "--report-to", "test@example.com"]):
            main()
    
    mock_reporter.send_report.assert_called_once()
    args, _ = mock_reporter.send_report.call_args
    assert args[2] == "test@example.com"
    captured = capsys.readouterr()
    assert "Triggering report delivery" in captured.out

def test_cli_peer_command():
    """Test the peer subcommand."""
    mock_mcp_server = MagicMock()
    with patch.dict("sys.modules", {"src.network.mcp_server": mock_mcp_server}):
        with patch.object(sys, "argv", ["src.cli", "peer", "--role", "thief", "--port", "8802", "--opponent-url", "http://fake"]):
            main()
    
    assert os.environ.get("OPPONENT_URL") == "http://fake"
    mock_mcp_server.mcp.run.assert_called_once_with(transport="sse", host="0.0.0.0", port=8802)
