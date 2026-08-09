"""DOS detector and circuit breaker."""
import time
from typing import Dict, List

class DOSDetector:
    def __init__(self, max_requests_per_window: int = 50, window_sec: float = 2.0):
        self.max_requests = max_requests_per_window
        self.window_sec = window_sec
        self.request_timestamps: List[float] = []
        self.locked = False

    def record_and_check(self) -> bool:
        if self.locked:
            return False
        now = time.monotonic()
        self.request_timestamps = [t for t in self.request_timestamps if now - t <= self.window_sec]
        self.request_timestamps.append(now)
        if len(self.request_timestamps) > self.max_requests:
            self.locked = True
            return False
        return True

    def reset(self) -> None:
        self.request_timestamps.clear()
        self.locked = False
