import json
import traceback
import asyncio
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from fastapi import FastAPI, Request, Response
import uvicorn

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from src.core.orchestrator import ThiefOrchestrator
from src.strategy.police_brain import MyPoliceBrain
from src.domain.scent import ScentTracker
from src.domain.belief import BayesianBeliefGrid
from src.shared.constants import THIEF_START_POS, COP_START_POS, MAX_MOVES, GRID_SIZE
from src.infra.reporter import GameReporter

app = FastAPI()

TERMS = {
  "axis_origin_corner": "top-left",
  "axis_start_index": 0,
  "barriers_max": 14,
  "board_size": 7,
  "cop_start": [0, 0],
  "decay_per_step": 0.1,
  "emit_intensity": 0.9,
  "hint_max_words": 15,
  "max_steps": 35,
  "min_center_intensity": 0.5,
  "num_games": 6,
  "setting": "Haifa",
  "smell_grid_size": 5,
  "thief_start": [3, 3]
}

def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def commit_of(obj: dict, nonce: str) -> str:
    return hashlib.sha256((canonical(obj) + "|" + nonce).encode("utf-8")).hexdigest()

class GameState:
    def __init__(self):
        self.game_count = 0
        self.step = 0
        self.opponent_url = "https://hint-prep-nokia-brochures.trycloudflare.com/mcp"
        self.running = False
        self.turn_queue = asyncio.Queue()
        self.game_task = None
        self.last_cop_claim = None
        self.caught_by_cop = False
        self.sub_games_results = []

state = GameState()

def get_move_str(old_pos, new_pos):
    dy = new_pos[0] - old_pos[0]
    dx = new_pos[1] - old_pos[1]
    if dy == -1: return "MOVE:N"
    if dy == 1: return "MOVE:S"
    if dx == 1: return "MOVE:E"
    if dx == -1: return "MOVE:W"
    return "STAY"

async def game_loop():
    print("[GAME LOOP] Connecting to opponent via fastmcp Client...")
    
    connected = False
    while not connected:
        try:
            mcp_client_ctx = Client(StreamableHttpTransport(state.opponent_url))
            await mcp_client_ctx.__aenter__()
            mcp_client = mcp_client_ctx
            connected = True
            print("[GAME LOOP] Connected!")
        except Exception as e:
            print(f"[GAME LOOP] Connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            
    try:
        print("[GAME LOOP] Starting 6 games...")
        state.running = True
        state.sub_games_results = []
        
        for game in range(6):
            sub_game = game + 1
            my_role = "thief" if game % 2 == 0 else "police"
            opponent_role = "police" if my_role == "thief" else "thief"
            
            print(f"\n{'='*40}\nStarting Game {sub_game}/6 - Playing as {my_role.upper()}\n{'='*40}")
            
            # NEGOTIATE
            n_nonce = secrets.token_hex(16)
            n_signature = commit_of(TERMS, n_nonce)
            neg_msg = {
                "message": {
                    "terms": TERMS,
                    "nonce": n_nonce,
                    "signature": n_signature,
                    "group_id": "amirmtan",
                    "role": my_role,
                    "sub_game_number": sub_game,
                    "identity": {
                        "group_id": "amirmtan", "group_name": "amirmtan",
                        "git_commit_hash": GameReporter.get_git_commit(),
                        "github_commit": GameReporter.get_git_commit(),
                        "members": ["Qusai Lela", "Amir Mtanes"],
                        "mcp_servers": {
                            "cop": "https://further-favourite-theft-stars.trycloudflare.com/mcp",
                            "thief": "https://further-favourite-theft-stars.trycloudflare.com/mcp"
                        }, "llm_model": "template", "code_version": "1.00", "first_mover": "thief",
                        "config_sha256": "3835f6a137620d8d98ab3925b2d1ed397d2d20d23bb9ba857bcd104284aac443",
                        "scent_model_sha256": "ea7225f5d71989add99a0057287342b7c5b86ab4efffd1608da25d0e368c0a28"
                    },
                    "first_mover": "thief",
                    "config_sha256": "3835f6a137620d8d98ab3925b2d1ed397d2d20d23bb9ba857bcd104284aac443",
                    "scent_model_sha256": "ea7225f5d71989add99a0057287342b7c5b86ab4efffd1608da25d0e368c0a28",
                    "code_version": "1.00"
                }
            }
            print(f"[GAME LOOP] Negotiating Game {sub_game}...")
            neg_res = await mcp_client.call_tool("negotiate", neg_msg)
            print(f"[CLIENT] Sent negotiate -> {neg_res}")
            
            # STATE INIT
            audit_log = []
            thief_pos = tuple(THIEF_START_POS)
            cop_pos = tuple(COP_START_POS)
            
            if my_role == "thief":
                orchestrator = ThiefOrchestrator(start_pos=THIEF_START_POS, grid_size=GRID_SIZE)
                thief_scent = ScentTracker(GRID_SIZE)
            else:
                cop_brain = MyPoliceBrain(start_pos=COP_START_POS, grid_size=GRID_SIZE)
                cop_scent = ScentTracker(GRID_SIZE)
                cop_belief = BayesianBeliefGrid(GRID_SIZE)
            
            end_reason = 'survival'
            state.caught_by_cop = False
            state.last_cop_claim = None
            
            for step in range(MAX_MOVES):
                step_idx = step + 1
                state.step = step_idx
                
                if my_role == "thief":
                    # THIEF LOGIC
                    t_state = {"step": step, "my_position": thief_pos}
                    h_commit, t_nonce, chosen_pos = orchestrator.compute_and_commit(t_state)
                    move_str = get_move_str(thief_pos, chosen_pos)
                    hint = orchestrator.audit_log[-1]["hint"]
                    
                    caught = state.caught_by_cop
                    claim_response = {"claim": state.last_cop_claim, "caught": caught} if state.last_cop_claim else None
                    
                    payload = {
                        'step': step_idx,
                        'role': 'thief',
                        'state': f'grid={GRID_SIZE};self=[{chosen_pos[0]}, {chosen_pos[1]}]',
                        'move': move_str,
                        'intent': 'truth',
                        'hint': hint,
                        'sub_game': sub_game,
                        'sub_game_number': sub_game
                    }
                    if claim_response:
                        payload['claim_response'] = claim_response
                        
                    t_nonce_actual = secrets.token_hex(16)
                    commit_hash = commit_of(payload, t_nonce_actual)
                    
                    audit_log.append({
                        "payload": payload,
                        "nonce": t_nonce_actual,
                        "commit": commit_hash
                    })
                    
                    thief_pos = chosen_pos
                    thief_scent.update_scent(thief_pos)
                    
                    turn_msg = {
                        "message": {
                            "step": step_idx,
                            "sender": "thief",
                            "hint": hint,
                            "smell_grid": {f"{r},{c}": thief_scent.get_matrix()[r][c] for r in range(GRID_SIZE) for c in range(GRID_SIZE)},
                            "commit": commit_hash,
                            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                            "barrier_placed": None,
                            "capture_claim": None,
                            "claim_response": claim_response,
                            "win_claim": {"type": "survival"} if step_idx == MAX_MOVES and not caught else None
                        }
                    }
                    
                    print(f"[GAME LOOP] Sending Thief turn {step_idx}...")
                    await mcp_client.call_tool("receive_turn", turn_msg)
                    
                    if caught:
                        print(f"[GAME LOOP] Thief was caught! Ending sub-game.")
                        end_reason = "capture"
                        break
                    
                    if step_idx == MAX_MOVES:
                        print(f"[GAME LOOP] Thief survival at step 35! Ending sub-game.")
                        end_reason = "survival"
                        break
                    
                    print(f"[GAME LOOP] Waiting for Police turn {step_idx}...")
                    try:
                        cop_turn = await asyncio.wait_for(state.turn_queue.get(), timeout=180.0)
                        cop_grid = cop_turn.get("smell_grid", {})
                        if isinstance(cop_grid, str):
                            try:
                                cop_grid = json.loads(cop_grid)
                            except:
                                cop_grid = {}
                        cop_hint = cop_turn.get("hint", "No hint")
                        print(f"[GAME LOOP] Received Police turn {step_idx}")
                        orchestrator.record_verified_turn((0,0), cop_hint)
                        
                        cop_claim = cop_turn.get("capture_claim")
                        state.last_cop_claim = cop_claim
                        if cop_claim and list(thief_pos) == list(cop_claim):
                            state.caught_by_cop = True
                        else:
                            state.caught_by_cop = False
                            
                    except asyncio.TimeoutError:
                        print(f"[GAME LOOP] Timed out waiting for Police turn {step_idx}!")
                        end_reason = "timeout"
                        break

                else:
                    # POLICE LOGIC
                    print(f"[GAME LOOP] Waiting for Thief turn {step_idx}...")
                    try:
                        thief_turn = await asyncio.wait_for(state.turn_queue.get(), timeout=180.0)
                        thief_hint = thief_turn.get("hint", "")
                        print(f"[GAME LOOP] Received Thief turn {step_idx}")
                        
                        claim_resp = thief_turn.get("claim_response")
                        if claim_resp and claim_resp.get("caught"):
                            print("[GAME LOOP] We caught the thief! Ending sub-game.")
                            end_reason = "capture"
                            break
                            
                        if thief_turn.get("win_claim") == {"type": "survival"}:
                            print("[GAME LOOP] Thief claims survival at step 35! Ending sub-game.")
                            end_reason = "survival"
                            break
                    except asyncio.TimeoutError:
                        print(f"[GAME LOOP] Timed out waiting for Thief turn {step_idx}!")
                        end_reason = "timeout"
                        break
                    
                    cop_estimated_thief = cop_belief.get_most_likely_position()
                    c_state = {"step": step, "my_position": cop_pos, "thief_pos": cop_estimated_thief}
                    
                    chosen_pos = cop_brain._decide_move(c_state)
                    move_str = get_move_str(cop_pos, chosen_pos)
                    hint = f"Movement is happening"
                    
                    payload = {
                        'step': step_idx,
                        'role': 'police',
                        'state': f'grid={GRID_SIZE};self=[{chosen_pos[0]}, {chosen_pos[1]}]',
                        'move': move_str,
                        'intent': 'pursuit',
                        'hint': hint,
                        'sub_game': sub_game,
                        'sub_game_number': sub_game,
                        'capture_claim': list(chosen_pos)
                    }
                    
                    c_nonce_actual = secrets.token_hex(16)
                    commit_hash = commit_of(payload, c_nonce_actual)
                    
                    audit_log.append({
                        "payload": payload,
                        "nonce": c_nonce_actual,
                        "commit": commit_hash
                    })
                    
                    cop_pos = chosen_pos
                    cop_scent.update_scent(cop_pos)
                    
                    turn_msg = {
                        "message": {
                            "step": step_idx,
                            "sender": "police",
                            "hint": hint,
                            "smell_grid": {f"{r},{c}": cop_scent.get_matrix()[r][c] for r in range(GRID_SIZE) for c in range(GRID_SIZE)},
                            "commit": commit_hash,
                            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                            "barrier_placed": None,
                            "capture_claim": list(cop_pos),
                            "claim_response": None,
                            "win_claim": None
                        }
                    }
                    
                    print(f"[GAME LOOP] Sending Police turn {step_idx}...")
                    await mcp_client.call_tool("receive_turn", turn_msg)
            
            print(f"[GAME LOOP] Finished Game {sub_game}/6. Sending submit_audit...")
            
            # Record result
            my_score = 0
            opp_score = 0
            if end_reason == "capture":
                if my_role == "police":
                    my_score = 20
                    opp_score = 5
                    winner = "amirmtan"
                else:
                    my_score = 5
                    opp_score = 20
                    winner = "GRP00001"
            elif end_reason == "survival":
                if my_role == "thief":
                    my_score = 10
                    opp_score = 5
                    winner = "amirmtan"
                else:
                    my_score = 5
                    opp_score = 10
                    winner = "GRP00001"
            else:
                my_score = 0
                opp_score = 0
                winner = None
            
            sub_game_result = {
                "result": end_reason,
                "roles": {"GRP00001": opponent_role, "amirmtan": my_role},
                "score": {"GRP00001": opp_score, "amirmtan": my_score},
                "sub_game_number": sub_game,
                "winner_group": winner
            }
            state.sub_games_results.append(sub_game_result)
            
            try:
                audit_msg = {
                    "payload": {
                        "sender": my_role,
                        "records": audit_log,
                        "result_claim": end_reason,
                        "sub_game": sub_game,
                        "sub_game_number": sub_game
                    }
                }
                audit_res = await mcp_client.call_tool("submit_audit", audit_msg)
                print(f"[CLIENT] Sent submit_audit -> {audit_res}")
            except Exception as e:
                print(f"[GAME LOOP] Failed to send submit_audit: {e}")
                
            await asyncio.sleep(2)

        print("[GAME LOOP] All 6 games finished! Sending series consensus...")
        
        # Calculate aggregates
        total_grp = sum(sg["score"]["GRP00001"] for sg in state.sub_games_results)
        total_amir = sum(sg["score"]["amirmtan"] for sg in state.sub_games_results)
        won_grp = sum(1 for sg in state.sub_games_results if sg["winner_group"] == "GRP00001")
        won_amir = sum(1 for sg in state.sub_games_results if sg["winner_group"] == "amirmtan")
        ties = 6 - won_grp - won_amir
        
        series_tie = False
        winner_group = None
        if total_grp == total_amir:
            series_tie = True
            total_grp += 2
            total_amir += 2
        elif total_grp > total_amir:
            winner_group = "GRP00001"
        else:
            winner_group = "amirmtan"
        
        consensus_obj = {
            "aggregate": {
                "total_score": {"GRP00001": total_grp, "amirmtan": total_amir},
                "sub_games_won": {"GRP00001": won_grp, "amirmtan": won_amir},
                "ties": ties,
                "winner_group": winner_group,
                "series_tie": series_tie
            },
            "game_id": "GRP00001-vs-amirmtan",
            "sub_games": state.sub_games_results
        }
        
        # Hash EXACTLY using specified spaced JSON
        consensus_str = json.dumps(consensus_obj, sort_keys=True, ensure_ascii=False)
        consensus_sha = hashlib.sha256(consensus_str.encode('utf-8')).hexdigest()
        
        # Write to file so user can copy-paste exact JSON to opponent easily
        with open("series_consensus.json", "w", encoding="utf-8") as f:
            f.write(consensus_str)
            
        # Add counted flags for lecturer email
        consensus_obj["match_mode"] = "counted"
        consensus_obj["lecturer_report_sent"] = True
        
        # Send lecturer email
        try:
            print("[GAME LOOP] Attempting to send report via Gmail API...")
            GameReporter.send_report(
                game_result=consensus_obj,
                game_id="GRP00001-vs-amirmtan",
                lecturer_email="rmisegal+uoh26finalgame@gmail.com"
            )
        except Exception as e:
            print(f"[GAME LOOP] Email delivery failed: {e}")
        
        try:
            audit_msg = {
                "payload": {
                    "sender": "thief",
                    "records": [],
                    "result_claim": "series_consensus",
                    "consensus_sha": consensus_sha
                }
            }
            await mcp_client.call_tool("submit_audit", audit_msg)
            print(f"[CLIENT] Sent series_consensus -> success")
        except Exception as e:
            print(f"[GAME LOOP] Failed to send series_consensus: {e}")

    except Exception as e:
        print(f"[GAME LOOP] Exception in game loop: {e}")
        traceback.print_exc()
    finally:
        if connected:
            await mcp_client_ctx.__aexit__(None, None, None)

def negotiate(message: dict) -> dict:
    print(f"[SERVER] Negotiate received: {message}", flush=True)
    if not state.running:
        state.game_task = asyncio.create_task(game_loop())
    return {"ok": True}

def receive_turn(message: dict) -> dict:
    print(f"[SERVER] Receive turn: step {message.get('step')}")
    state.turn_queue.put_nowait(message.get("message", message)) # Fix extraction to handle both cases securely
    return {"ok": True}

def submit_audit(payload: dict) -> dict:
    print(f"[SERVER] Submit audit: {payload}")
    return {"ok": True}

def receive_control(message: dict) -> dict:
    print(f"[SERVER] Receive control: {message}", flush=True)
    if message.get("command") == "start":
        if not state.running:
            state.game_task = asyncio.create_task(game_loop())
    return {"ok": True}

tools_impl = {
    "negotiate": negotiate,
    "receive_turn": receive_turn,
    "submit_audit": submit_audit,
    "receive_control": receive_control
}

tools_schema = []
for k in tools_impl:
    if k == "submit_audit":
        tools_schema.append({
            "name": k,
            "description": k,
            "inputSchema": {
                "type": "object",
                "properties": {"payload": {"type": "object"}},
                "required": ["payload"]
            }
        })
    else:
        tools_schema.append({
            "name": k,
            "description": k,
            "inputSchema": {
                "type": "object",
                "properties": {"message": {"type": "object"}},
                "required": ["message"]
            }
        })

@app.post("/mcp")
async def handle_mcp_post(request: Request):
    try:
        req_data = await request.json()
        method = req_data.get("method")
        params = req_data.get("params", {})
        msg_id = req_data.get("id")
        
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "thief_peer", "version": "1.0.0"}}}
        elif method == "tools/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools_schema}}
        elif method == "tools/call" or method == "call_tool":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name in tools_impl:
                result = tools_impl[tool_name](**tool_args)
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Tool not found"}}
        elif method in tools_impl:
            result = tools_impl[method](**(params if isinstance(params, dict) else {}))
            return {"jsonrpc": "2.0", "id": msg_id, "result": result}
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
    except Exception as e:
        return {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e), "data": traceback.format_exc()}}

@app.get("/mcp")
@app.head("/mcp")
async def handle_mcp_head():
    return Response(content="MCP Server ready. Use POST.", status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8020)
