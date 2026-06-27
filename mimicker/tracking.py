import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class StubRecord:
    method: str
    path: str
    hit_count: int = 0


@dataclass
class UnmatchedRecord:
    method: str
    path: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )


class RequestTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._stubs: Dict[str, StubRecord] = {}
        self._unmatched: List[UnmatchedRecord] = []

    def register_stub(self, method: str, path: str):
        key = f"{method} {path}"
        with self._lock:
            self._stubs[key] = StubRecord(method=method, path=path)

    def record_hit(self, method: str, path: str):
        key = f"{method} {path}"
        with self._lock:
            if key in self._stubs:
                self._stubs[key].hit_count += 1

    def record_unmatched(self, method: str, path: str):
        with self._lock:
            self._unmatched.append(UnmatchedRecord(method=method, path=path))

    def report(self) -> dict:
        with self._lock:
            stubs = list(self._stubs.values())
            unmatched = list(self._unmatched)

        used = [s for s in stubs if s.hit_count > 0]
        unused = [s for s in stubs if s.hit_count == 0]

        return {
            "summary": {
                "total_stubs": len(stubs),
                "matched_stubs": len(used),
                "unmatched_requests": len(unmatched),
            },
            "stubs": [
                {"method": s.method, "path": s.path, "hit_count": s.hit_count}
                for s in stubs
            ],
            "unused_stubs": [
                {"method": s.method, "path": s.path}
                for s in unused
            ],
            "unmatched_requests": [
                {"method": r.method, "path": r.path, "timestamp": r.timestamp}
                for r in unmatched
            ],
        }

    def reset(self):
        with self._lock:
            for s in self._stubs.values():
                s.hit_count = 0
            self._unmatched.clear()
