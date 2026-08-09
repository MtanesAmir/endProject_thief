import pytest
import sys
from unittest.mock import patch
from src.cli import main
from src.core.match_runner import MatchRunner
from src.experiments.benchmark import run_benchmark

def test_match_runner():
    runner = MatchRunner(max_steps=5)
    res = runner.run_simulation()
    assert "outcome" in res
    assert "thief_score" in res

def test_benchmark():
    res = run_benchmark(rounds=2)
    assert res["rounds"] == 2

def test_cli_execution():
    with patch.object(sys, "argv", ["src.cli", "match", "--rounds", "1"]):
        main()
    with patch.object(sys, "argv", ["src.cli", "benchmark", "--rounds", "1"]):
        main()
    with patch.object(sys, "argv", ["src.cli", "hardware"]):
        main()
    with patch.object(sys, "argv", ["src.cli", "replay", "--log", "test.json"]):
        main()
    with patch.object(sys, "argv", ["src.cli"]):
        main()
