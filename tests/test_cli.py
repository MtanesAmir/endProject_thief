"""Comprehensive CLI tests covering all subcommands."""
import pytest
import sys
import json
import os
import tempfile
import hashlib
from unittest.mock import patch, MagicMock
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


def test_cli_match(capsys):
    """Test the match CLI subcommand."""
    with patch.object(sys, "argv", ["src.cli", "match"]):
        main()
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "outcome" in output
    assert "audit_log" in output
    assert "steps" in output


def test_cli_benchmark(capsys):
    """Test the benchmark CLI subcommand."""
    with patch.object(sys, "argv", ["src.cli", "benchmark", "--rounds", "2"]):
        main()
    captured = capsys.readouterr()
    assert "thief_wins" in captured.out
    assert "cop_wins" in captured.out


def test_cli_replay_valid(tmp_path, capsys):
    """Test the replay CLI subcommand with a valid log."""
    # Build a valid replay entry
    move = "(3, 3)"
    nonce = "abc123"
    state = {}
    hint = ""
    payload = {"intent": hint, "move": move, "state": state}
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    seed = f"{s}|{nonce}"
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    log = [{"move": move, "nonce": nonce, "commit": h, "state": state, "hint": hint}]

    log_file = tmp_path / "test_log.json"
    log_file.write_text(json.dumps(log))

    with patch.object(sys, "argv", ["src.cli", "replay", "--log", str(log_file)]):
        main()
    captured = capsys.readouterr()
    assert "VERIFIED_OK" in captured.out


def test_cli_replay_tampered(tmp_path, capsys):
    """Test the replay CLI subcommand with a tampered log."""
    log = [{"move": "(3, 3)", "nonce": "abc", "commit": "bad_hash", "state": {}, "hint": ""}]
    log_file = tmp_path / "tampered_log.json"
    log_file.write_text(json.dumps(log))

    with patch.object(sys, "argv", ["src.cli", "replay", "--log", str(log_file)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_cli_replay_file_not_found():
    """Test the replay CLI with a non-existent file."""
    with patch.object(sys, "argv", ["src.cli", "replay", "--log", "nonexistent_file.json"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_cli_replay_invalid_json(tmp_path):
    """Test the replay CLI with invalid JSON."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("NOT VALID JSON {{{")

    with patch.object(sys, "argv", ["src.cli", "replay", "--log", str(bad_file)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
