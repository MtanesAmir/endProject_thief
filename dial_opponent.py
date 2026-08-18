import requests
import time
import json

url = 'https://propose-effectively-tomato-raises.trycloudflare.com/mcp'
terms = {
    'board_size': 7, 'smell_grid_size': 5, 'decay_per_step': 0.1, 'emit_intensity': 0.9,
    'min_center_intensity': 0.5, 'max_steps': 35, 'barriers_max': 14, 'setting': 'New York',
    'hint_max_words': 15, 'axis_origin_corner': 'top-left', 'axis_start_index': 0,
    'thief_start': [3, 3], 'cop_start': [0, 0], 'num_games': 6
}
p = {
    'jsonrpc': '2.0',
    'method': 'tools/call',
    'params': {'name': 'negotiate', 'arguments': {'message': terms}},
    'id': 1
}

started = time.time()
while time.time() - started < 120:
    try:
        r = requests.post(url, json=p, timeout=5)
        print(f"Status: {r.status_code}, Body: {r.text[:100]}")
        if r.status_code != 502:
            break
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(15)
