"""Test match runner pre-capture condition."""
import pytest
from unittest.mock import patch
from src.core.match_runner import MatchRunner
from src.shared.constants import COP_START_POS

def test_match_runner_pre_capture():
    """Test match runner when thief and cop start on same position."""
    with patch("src.core.match_runner.THIEF_START_POS", COP_START_POS):
        runner = MatchRunner(max_steps=5)
        res = runner.run_simulation()
        
    assert res["outcome"] == "COP_CAPTURE"
    assert res["steps"] == 0
