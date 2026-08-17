"""Gmail API integration for automated report generation."""
import json
import subprocess
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

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

        creds = None
        if os.path.exists('config/token.json'):
            creds = Credentials.from_authorized_user_file('config/token.json', SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('config/credentials.json'):
                    print("Error: config/credentials.json not found. Please provide Google OAuth secrets.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('config/token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)

            message = EmailMessage()
            message.set_content(f"Automated game report for match ID: {game_id}.")
            message['To'] = lecturer_email
            message['From'] = "thief.agent@example.com"
            message['Subject'] = f"Game Report: {game_id}"

            with open(filename, 'rb') as f:
                content = f.read()

            message.add_attachment(content, maintype='application', subtype='json', filename=filename)

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            from src.domain.gatekeeper import GatekeeperValidator
            if not GatekeeperValidator.global_limiter.acquire(1.0):
                print("Gmail API Rate limit exceeded. Throttling report delivery.")
                return

            send_message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(f'Report sent via Gmail API. Message Id: {send_message["id"]}')
        except Exception as e:
            print(f"Failed to send email report: {e}")
