"""Rate limiter & gatekeeper interfaces."""
import time
from typing import Callable, Any, Optional
from src.infra.rate_limiter import TokenBucketRateLimiter

class GatekeeperError(Exception):
    pass

class RateLimitExceeded(GatekeeperError):
    pass

class GatekeeperValidator:
    # 30 RPM limit using token bucket
    global_limiter = TokenBucketRateLimiter(capacity=30.0, refill_rate=0.5)

    @staticmethod
    def validate_request_size(payload: str, max_bytes: int = 65536) -> bool:
        return len(payload.encode("utf-8")) <= max_bytes

    @classmethod
    def enforce_rate_limit(cls, cost: float = 1.0) -> None:
        if not cls.global_limiter.acquire(cost):
            raise RateLimitExceeded("Global API rate limit exceeded (30 RPM maximum).")
