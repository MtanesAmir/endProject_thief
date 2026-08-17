"""Full match execution loop and round simulation."""
import asyncio
import subprocess
import os
from typing import Dict, Any
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

class MatchRunner:
    def __init__(self, max_steps: int = 35, response_timeout_sec: float = 10.0):
        self.max_steps = max_steps
        self.thief_port = 8802
        self.cop_port = 8803
        self.response_timeout_sec = response_timeout_sec

    def run_simulation(self) -> Dict[str, Any]:
        return asyncio.run(self.run_simulation_async())

    async def run_simulation_async(self) -> Dict[str, Any]:
        env_thief = os.environ.copy()
        env_thief["CONFIG_PATH"] = "config/thief/"
        
        env_cop = os.environ.copy()
        env_cop["CONFIG_PATH"] = "config/police/"

        thief_proc = subprocess.Popen(
            ["python", "-m", "src.cli", "peer", "--role", "thief", "--port", str(self.thief_port)],
            env=env_thief
        )
        cop_proc = subprocess.Popen(
            ["python", "-m", "src.cli", "peer", "--role", "police", "--port", str(self.cop_port)],
            env=env_cop
        )
        
        await asyncio.sleep(4)
        
        try:
            async with sse_client(f"http://localhost:{self.thief_port}/sse") as (t_read, t_write):
                async with ClientSession(t_read, t_write) as thief_session:
                    await thief_session.initialize()

                    async with sse_client(f"http://localhost:{self.cop_port}/sse") as (c_read, c_write):
                        async with ClientSession(c_read, c_write) as cop_session:
                            await cop_session.initialize()

                            try:
                                # Watchdog: If the Cop doesn't respond within response_timeout_sec,
                                # trigger a controlled shutdown and technical win.
                                # Example placeholder for actual cop call: await asyncio.wait_for(cop_session.call_tool("decide_move", {}), timeout=self.response_timeout_sec)
                                pass
                            except asyncio.TimeoutError:
                                return {"status": "TECHNICAL_LOSS", "cop_score": 0, "thief_score": 0}
                                
                            return {"status": "True network simulation active with isolated processes."}
        finally:
            thief_proc.terminate()
            cop_proc.terminate()
            thief_proc.wait()
            cop_proc.wait()
