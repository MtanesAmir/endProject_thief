"""Command-line interface entrypoint for Thief peer."""
import argparse
import sys
import json
from src.core.match_runner import MatchRunner
from src.experiments.benchmark import run_benchmark
from src.gui.replay_verifier import ReplayVerifier
from src.domain.hardware import get_hardware_declaration

def main():
    parser = argparse.ArgumentParser(description="Thief Peer CLI")
    subparsers = parser.add_subparsers(dest="command")

    peer_p = subparsers.add_parser("peer")
    peer_p.add_argument("--role", default="thief")
    peer_p.add_argument("--port", type=int, default=8802)

    match_p = subparsers.add_parser("match")
    match_p.add_argument("--rounds", type=int, default=1)
    match_p.add_argument("--report-to", type=str, default="")

    bench_p = subparsers.add_parser("benchmark")
    bench_p.add_argument("--rounds", type=int, default=10)

    replay_p = subparsers.add_parser("replay")
    replay_p.add_argument("--log", required=True)

    hw_p = subparsers.add_parser("hardware")

    args = parser.parse_args()
    if args.command == "match":
        runner = MatchRunner()
        res = runner.run_simulation()
        print(json.dumps(res, indent=2))
        
        if args.report_to:
            from src.infra.reporter import GameReporter
            import uuid
            game_id = str(uuid.uuid4())[:8]
            print(f"Triggering report delivery to {args.report_to}...")
            GameReporter.send_report(res, game_id, args.report_to)
    elif args.command == "benchmark":
        print(run_benchmark(args.rounds))
    elif args.command == "hardware":
        print(json.dumps(get_hardware_declaration(), indent=2))
    elif args.command == "replay":
        try:
            with open(args.log, "r", encoding="utf-8") as f:
                log_data = json.load(f)
                
            result = ReplayVerifier.verify_log(log_data)
            print(json.dumps(result, indent=2))
            
            if result.get("status") == "TAMPERED":
                print("========================================")
                print("!! CRITICAL WARNING: TAMPERED LOG DETECTED !!")
                print("========================================")
                sys.exit(1)
                
        except FileNotFoundError:
            print(f"Error: Log file '{args.log}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Log file '{args.log}' contains invalid JSON.")
            sys.exit(1)
    elif args.command == "peer":
        from src.p2p.server import create_p2p_server
        print(f"Starting {args.role} peer on port {args.port}...")
        server = create_p2p_server(name=args.role, port=args.port)
        server.run()
    else:
        print("Thief Peer ready.")

if __name__ == "__main__":
    main()
