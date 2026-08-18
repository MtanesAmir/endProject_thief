import asyncio, hashlib, json, secrets
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

TERMS = {
  'board_size': 7, 'smell_grid_size': 5, 'decay_per_step': 0.1,
  'emit_intensity': 0.9, 'min_center_intensity': 0.5, 'max_steps': 35,
  'barriers_max': 14, 'setting': 'New York', 'hint_max_words': 15,
  'axis_origin_corner': 'top-left', 'axis_start_index': 0,
  'thief_start': [3, 3], 'cop_start': [0, 0], 'num_games': 6
}
nonce = secrets.token_hex(16)
body = json.dumps(TERMS, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
signature = hashlib.sha256(f'{body}|{nonce}'.encode()).hexdigest()
message = {
  'terms': TERMS, 'nonce': nonce, 'signature': signature,
  'group_id': 'amirmtan', 'role': 'thief', 'sub_game_number': 1,
  'identity': {'group_id': 'amirmtan', 'mcp_servers': {'cop': 'https://propose-effectively-tomato-raises.trycloudflare.com/mcp', 'thief': 'https://connections-polls-result-streets.trycloudflare.com/mcp'}}, 'first_mover': 'thief'
}
URL = 'https://propose-effectively-tomato-raises.trycloudflare.com/mcp'

async def main():
    while True:
        try:
            async with Client(StreamableHttpTransport(URL)) as c:
                print("Connected! Tools:")
                print(sorted(t.name for t in await c.list_tools()))
                print("Negotiating...")
                print(await c.call_tool('negotiate', {'message': message}))
                break
        except Exception as e:
            print(f"Failed: {type(e).__name__} - {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

asyncio.run(main())
