import pytest
from src.infra.rate_limiter import TokenBucketRateLimiter
from src.infra.dos_detector import DOSDetector

def test_rate_limiter():
    limiter = TokenBucketRateLimiter(capacity=2.0, refill_rate=0.1)
    assert limiter.acquire(1.0) is True
    assert limiter.acquire(1.0) is True
    assert limiter.acquire(1.0) is False

def test_dos_detector():
    dos = DOSDetector(max_requests_per_window=3, window_sec=1.0)
    assert dos.record_and_check() is True
    assert dos.record_and_check() is True
    assert dos.record_and_check() is True
    assert dos.record_and_check() is False
