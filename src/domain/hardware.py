"""Step-0 Hardware auto-discovery and platform declaration."""
import os
import platform
import subprocess
from typing import Dict, Any

def get_hardware_declaration(group_id: str = "thief-team", role: str = "thief") -> Dict[str, Any]:
    git_hash = "unknown"
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            git_hash = res.stdout.strip()
    except Exception:
        pass

    return {
        "group_id": group_id,
        "role": role,
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count() or 1,
        "python_version": platform.python_version(),
        "git_commit_hash": git_hash,
    }
