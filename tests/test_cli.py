import pytest
import sys
from unittest.mock import patch
from src.cli import main
from src.core.match_runner import MatchRunner
from src.experiments.benchmark import run_benchmark

def test_match_runner():
    runner = MatchRunner(max_steps=5)
    res = runner.run_simulation()
    assert isinstance(res, dict)
    assert "outcome" in res
    assert "thief_score" in res or "cop_score" in res
    assert "steps" in res
    assert "audit_log" in res
    assert res["steps"] <= 5

def test_match_runner_full_game():
    runner = MatchRunner(max_steps=35)
    res = runner.run_simulation()
    assert res["outcome"] in ("COP_CAPTURE", "THIEF_SURVIVAL")

def test_benchmark():
    res = run_benchmark(rounds=2)
    assert res["rounds"] == 2
    assert "thief_wins" in res
    assert "cop_wins" in res
    assert "thief_win_rate" in res

def test_cli_hardware():
    with patch.object(sys, "argv", ["src.cli", "hardware"]):
        main()

def test_cli_no_command():
    with patch.object(sys, "argv", ["src.cli"]):
        main()
