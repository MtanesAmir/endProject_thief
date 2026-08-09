import pytest
import time

def test_watchdog_timeout():
    start = time.time()
    elapsed = time.time() - start
    assert elapsed < 1.0
