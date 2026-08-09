import pytest
import os
from src.automation.reporting import GmailReporter, generate_match_artifacts

def test_reporting(tmp_path):
    out = generate_match_artifacts("g123", {"winner": "thief"}, output_dir=str(tmp_path))
    assert os.path.exists(out["declaration"])
    assert os.path.exists(out["result"])

def test_gmail_reporter(tmp_path):
    reporter = GmailReporter(
        credentials_path=str(tmp_path / "credentials.json"),
        token_path=str(tmp_path / "token.json"),
        evaluator_email="test@example.com"
    )
    summary = {"outcome": "THIEF_SURVIVAL", "final_score": 10, "total_steps": 35}
    reports = reporter.compile_match_reports(summary)
    assert "declaration_thief.json" in reports
    assert "result_thief.json" in reports

    res = reporter.send_match_report(summary)
    assert res["status"] == "SENT"
