"""Gmail API integration for automated report generation."""
import json
import subprocess
import os
import smtplib
from email.message import EmailMessage



class GameReporter:
    @staticmethod
    def get_git_commit() -> str:
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        except Exception:
            return "unknown_commit"

    @staticmethod
    def send_report(game_result: dict, game_id: str, lecturer_email: str) -> None:
        commit_hash = GameReporter.get_git_commit()
        game_result["thief_commit"] = commit_hash
        game_result["cop_commit"] = commit_hash
        
        # In a real run, total_tokens would be pulled from the central LLMProvider tracker
        game_result["total_llm_tokens"] = game_result.get("total_llm_tokens", 0)
        
        filename = f"result_{game_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(game_result, f, indent=2)

        if not os.path.exists('config/app_password.txt'):
            print("Error: config/app_password.txt not found. Please create it and paste your Google App Password inside.")
            return
            
        with open('config/app_password.txt', 'r', encoding='utf-8') as f:
            app_password = f.read().strip()

        try:
            message = EmailMessage()
            message.set_content(f"Automated game report for match ID: {game_id}.")
            message['To'] = lecturer_email
            
            sender_email = "qusai.amara9@gmail.com"
            message['From'] = sender_email
            message['Subject'] = f"Game Report: {game_id}"

            with open(filename, 'rb') as f:
                content = f.read()

            message.add_attachment(content, maintype='application', subtype='json', filename=filename)

            from src.domain.gatekeeper import GatekeeperValidator
            if not GatekeeperValidator.global_limiter.acquire(1.0):
                print("SMTP Rate limit exceeded. Throttling report delivery.")
                return

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender_email, app_password)
                smtp_server.send_message(message)
                
            print(f'Report sent via SMTP.')
        except Exception as e:
            print(f"Failed to send email report via SMTP: {e}")
