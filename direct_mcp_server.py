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

app = FastAPI()

class GameState:
    def __init__(self):
        self.game_count = 0
        self.step = 0
        self.opponent_url = "https://propose-effectively-tomato-raises.trycloudflare.com/mcp"
        self.running = False
        self.turn_queue = asyncio.Queue()
        self.game_task = None

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
        print("[GAME LOOP] Starting 6 warmup games...")
        state.running = True
        
        for game in range(6):
            sub_game = game + 1
            my_role = "thief" if game % 2 == 0 else "police"
            
            print(f"\n{'='*40}\nStarting Game {sub_game}/6 - Playing as {my_role.upper()}\n{'='*40}")
            
            # NEGOTIATE
            neg_terms = {
                'board_size': 7, 'smell_grid_size': 5, 'decay_per_step': 0.1,
                'emit_intensity': 0.9, 'min_center_intensity': 0.5, 'max_steps': 35,
                'barriers_max': 14, 'setting': 'New York', 'hint_max_words': 15,
                'axis_origin_corner': 'top-left', 'axis_start_index': 0,
                'thief_start': [3, 3], 'cop_start': [0, 0], 'num_games': 6
            }
            n_nonce = secrets.token_hex(16)
            n_body = json.dumps(neg_terms, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            n_signature = hashlib.sha256(f'{n_body}|{n_nonce}'.encode()).hexdigest()
            neg_msg = {
                "message": {
                    "terms": neg_terms,
                    "nonce": n_nonce,
                    "signature": n_signature,
                    "group_id": "amirmtan",
                    "role": my_role,
                    "sub_game_number": sub_game,
                    "identity": {
                        "group_id": "amirmtan", "group_name": "amirmtan",
                        "git_commit_hash": "fe093bfd2ad2210741b17f69da917121ac86eb3d",
                        "github_commit": "fe093bfd2ad2210741b17f69da917121ac86eb3d",
                        "members": ["Qusai Lela", "Amir Mtanes"],
                        "mcp_servers": {
                            "cop": "https://connections-polls-result-streets.trycloudflare.com/mcp",
                            "thief": "https://connections-polls-result-streets.trycloudflare.com/mcp"
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
            else:
                cop_brain = MyPoliceBrain(start_pos=COP_START_POS, grid_size=GRID_SIZE)
                cop_scent = ScentTracker(GRID_SIZE)
                cop_belief = BayesianBeliefGrid(GRID_SIZE)
            
            # PLAY TURNS
            for step in range(MAX_MOVES):
                step_idx = step + 1
                state.step = step_idx
                
                if my_role == "thief":
                    # THIEF LOGIC
                    t_state = {"step": step, "my_position": thief_pos}
                    h_commit, t_nonce, chosen_pos = orchestrator.compute_and_commit(t_state)
                    move_str = get_move_str(thief_pos, chosen_pos)
                    hint = orchestrator.audit_log[-1]["hint"]
                    
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
                    body = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
                    commit_hash = hashlib.sha256(f'{body}|{t_nonce}'.encode()).hexdigest()
                    
                    audit_log.append({
                        "payload": payload,
                        "nonce": t_nonce,
                        "commit": commit_hash
                    })
                    
                    turn_msg = {
                        "message": {
                            "step": step_idx,
                            "sender": "thief",
                            "hint": hint,
                            "smell_grid": {},
                            "commit": commit_hash,
                            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                            "barrier_placed": None,
                            "capture_claim": None,
                            "claim_response": None,
                            "win_claim": None
                        }
                    }
                    
                    thief_pos = chosen_pos
                    print(f"[GAME LOOP] Sending Thief turn {step_idx}...")
                    await mcp_client.call_tool("receive_turn", turn_msg)
                    
                    print(f"[GAME LOOP] Waiting for Police turn {step_idx}...")
                    try:
                        cop_turn = await asyncio.wait_for(state.turn_queue.get(), timeout=30.0)
                        cop_grid = cop_turn.get("smell_grid", {})
                        if isinstance(cop_grid, str):
                            try:
                                cop_grid = json.loads(cop_grid)
                            except:
                                cop_grid = {}
                        cop_hint = cop_turn.get("hint", "No hint")
                        print(f"[GAME LOOP] Received Police turn {step_idx}")
                        orchestrator.record_verified_turn((0,0), cop_hint) # We don't have cop move, use 0,0
                    except asyncio.TimeoutError:
                        print(f"[GAME LOOP] Timed out waiting for Police turn {step_idx}!")
                        break

                else:
                    # POLICE LOGIC
                    print(f"[GAME LOOP] Waiting for Thief turn {step_idx}...")
                    try:
                        thief_turn = await asyncio.wait_for(state.turn_queue.get(), timeout=30.0)
                        thief_hint = thief_turn.get("hint", "")
                        print(f"[GAME LOOP] Received Thief turn {step_idx}")
                    except asyncio.TimeoutError:
                        print(f"[GAME LOOP] Timed out waiting for Thief turn {step_idx}!")
                        break
                    
                    cop_estimated_thief = cop_belief.get_most_likely_position()
                    c_state = {"step": step, "my_position": cop_pos, "thief_pos": cop_estimated_thief}
                    
                    chosen_pos = cop_brain._decide_move(c_state)
                    move_str = get_move_str(cop_pos, chosen_pos)
                    c_nonce = secrets.token_hex(16)
                    hint = f"Movement is happening"
                    
                    payload = {
                        'step': step_idx,
                        'role': 'police',
                        'state': f'grid={GRID_SIZE};self=[{chosen_pos[0]}, {chosen_pos[1]}]',
                        'move': move_str,
                        'intent': 'pursuit',
                        'hint': hint,
                        'sub_game': sub_game,
                        'sub_game_number': sub_game
                    }
                    body = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
                    commit_hash = hashlib.sha256(f'{body}|{c_nonce}'.encode()).hexdigest()
                    
                    audit_log.append({
                        "payload": payload,
                        "nonce": c_nonce,
                        "commit": commit_hash
                    })
                    
                    cop_pos = chosen_pos
                    cop_scent.update_scent(thief_pos) # Don't really know it, but we can't update scent without it. Pass.
                    
                    turn_msg = {
                        "message": {
                            "step": step_idx,
                            "sender": "police",
                            "hint": hint,
                            "smell_grid": cop_scent.get_matrix(),
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
            
            try:
                audit_msg = {
                    "payload": {
                        "sender": my_role,
                        "records": audit_log,
                        "result_claim": "survival",
                        "sub_game": sub_game,
                        "sub_game_number": sub_game
                    }
                }
                audit_res = await mcp_client.call_tool("submit_audit", audit_msg)
                print(f"[CLIENT] Sent submit_audit -> {audit_res}")
            except Exception as e:
                print(f"[GAME LOOP] Failed to send submit_audit: {e}")
                
            await asyncio.sleep(2)

        print("[GAME LOOP] All 6 games finished!")
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
    state.turn_queue.put_nowait(message)
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

tools_schema = [
    {"name": k, "description": k, "inputSchema": {"type": "object", "properties": {"message": {"type": "object"} if k != "submit_audit" else {"type": "object", "properties": {"payload": {"type": "object"}}}}, "required": ["message" if k != "submit_audit" else "payload"]}}
    for k in tools_impl
]

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
