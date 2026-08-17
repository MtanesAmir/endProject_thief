"""Thief Match Report Builder & Automated Gmail Reporter.

Compiles match artifacts (declaration_thief.json, config_thief.json, log_thief.json, result_thief.json)
and transmits match reports via OAuth 2.0 Gmail API to the evaluator.

Actual email delivery is delegated to ``GameReporter`` in ``src.infra.reporter``
to maintain a single responsibility split: this module *compiles*, reporter *sends*.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional
from src.shared.version import APP_VERSION


class GmailReporter:
    """Automated Gmail Reporter and Match Artifact Compiler for Thief Agent."""

    GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        evaluator_email: str = "rmisegal+uoh26finalgame@gmail.com",
    ):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.evaluator_email = evaluator_email

    def compile_match_reports(self, summary_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        timestamp = summary_data.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        commit_hash = summary_data.get("commit_hash", "0000000000000000000000000000000000000000")
        repo_url = summary_data.get("github_repo_url", "https://github.com/MtanesAmir/endProject_thief")

        declaration = {
            "artifact_type": "declaration",
            "agent_role": "Thief",
            "commit_hash": commit_hash,
            "github_repo_url": repo_url,
            "timestamp": timestamp,
            "signature": hashlib.sha256(f"declaration|Thief|{commit_hash}|{timestamp}".encode("utf-8")).hexdigest(),
        }

        config = {
            "artifact_type": "config",
            "agent_role": "Thief",
            "grid_size": summary_data.get("grid_size", 7),
            "timeout_ms": summary_data.get("timeout_ms", 50),
            "max_turns": summary_data.get("max_turns", 35),
            "thief_config": summary_data.get("thief_config", {"mode": "Dec-POMDP", "zero_trust": True}),
        }

        log = {
            "artifact_type": "log",
            "agent_role": "Thief",
            "total_steps": summary_data.get("total_steps", 0),
            "verified_ok": summary_data.get("verified_ok", True),
            "trajectory_summary": summary_data.get("trajectory", []),
        }

        result = {
            "artifact_type": "result",
            "agent_role": "Thief",
            "outcome": summary_data.get("outcome", "IN_PROGRESS"),
            "final_score": summary_data.get("final_score", 0),
            "token_consumption_stats": summary_data.get("token_stats", {"prompt_tokens": 0, "completion_tokens": 0}),
            "timestamp": timestamp,
        }

        return {
            "declaration_thief.json": declaration,
            "config_thief.json": config,
            "log_thief.json": log,
            "result_thief.json": result,
        }

    def send_match_report(
        self,
        summary_data: Dict[str, Any],
        recipient: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compile match artifacts and send via Gmail API.

        Delegates actual email delivery to ``GameReporter.send_report`` from
        ``src.infra.reporter``, avoiding duplicate sending logic.
        """
        recipient = recipient or self.evaluator_email
        artifacts = self.compile_match_reports(summary_data)
        subject = f"[Thief Match Report] Outcome: {summary_data.get('outcome', 'COMPLETED')}"
        body_payload = {"summary": summary_data, "artifacts": artifacts}

        try:
            from src.infra.reporter import GameReporter
            GameReporter.send_report(
                game_result=body_payload,
                game_id=summary_data.get("game_id", "unknown"),
                lecturer_email=recipient,
            )
            return {"status": "SENT", "mode": "GMAIL_API", "recipient": recipient, "subject": subject}
        except Exception as e:
            return {"status": "SEND_FAILED", "error": str(e), "recipient": recipient, "subject": subject}


def generate_match_artifacts(game_id: str, results: Dict[str, Any], output_dir: str = "results") -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    dec_path = os.path.join(output_dir, f"declaration_{game_id}.json")
    with open(dec_path, "w", encoding="utf-8") as f:
        json.dump({"game_id": game_id, "version": APP_VERSION, "status": "declared"}, f, indent=2)
    paths["declaration"] = dec_path

    res_path = os.path.join(output_dir, f"result_{game_id}.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    paths["result"] = res_path
    return paths
