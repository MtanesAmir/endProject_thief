"""Rate limiter & gatekeeper interfaces."""
import time
from typing import Callable, Any, Optional

class GatekeeperError(Exception):
    pass

class RateLimitExceeded(GatekeeperError):
    pass

class GatekeeperValidator:
    @staticmethod
    def validate_request_size(payload: str, max_bytes: int = 65536) -> bool:
        return len(payload.encode("utf-8")) <= max_bytes
