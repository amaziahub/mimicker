from dataclasses import dataclass, field
from time import time
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RateLimitConfig:
    max_requests: int
    window_seconds: float
    key_header: Optional[str] = None
    status_code: int = 429
    body: Any = None
    headers: Optional[List[Tuple[str, str]]] = None


class RateLimitTracker:
    def __init__(self):
        self._windows: Dict[str, List[float]] = {}

    def is_allowed(
        self, key: str, max_requests: int, window_seconds: float
    ) -> Tuple[bool, int, int]:
        now = time()
        cutoff = now - window_seconds
        timestamps = self._windows.get(key, [])
        timestamps = [t for t in timestamps if t > cutoff]
        remaining = max_requests - len(timestamps)
        reset_time = int(now) + int(window_seconds)
        if remaining > 0:
            timestamps.append(now)
            self._windows[key] = timestamps
            return True, remaining - 1, reset_time
        return False, 0, reset_time

    def reset(self):
        self._windows.clear()
