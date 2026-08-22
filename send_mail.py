import json
import os
import sys

from src.infra.reporter import GameReporter

def main():
    print("Loading consensus data...")
    if not os.path.exists("series_consensus.json"):
        print("Error: series_consensus.json not found!")
        sys.exit(1)
        
    with open("series_consensus.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data["match_mode"] = "counted"
    data["lecturer_report_sent"] = True
    
    print("Attempting to send email via SMTP...")
    
    try:
        GameReporter.send_report(
            game_result=data,
            game_id="GRP00001-vs-amirmtan",
            lecturer_email="rmisegal+uoh26finalgame@gmail.com"
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    main()
