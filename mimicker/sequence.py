import threading
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class SequenceStep:
    _status: int = 200
    _body: Any = None
    _headers: Optional[List[Tuple[str, str]]] = field(default=None)
    _delay: float = 0.0

    def status(self, code: int) -> "SequenceStep":
        self._status = code
        return self

    def body(self, content: Any) -> "SequenceStep":
        self._body = content
        return self

    def headers(self, headers: List[Tuple[str, str]]) -> "SequenceStep":
        self._headers = headers
        return self

    def delay(self, seconds: float) -> "SequenceStep":
        self._delay = seconds
        return self


class SequenceConfig:
    def __init__(self, steps: List[SequenceStep], cycle: bool = False):
        self._steps = steps
        self._cycle = cycle
        self._index = 0
        self._lock = threading.Lock()

    def next_step(self) -> SequenceStep:
        with self._lock:
            current = self._steps[self._index]
            if self._index < len(self._steps) - 1:
                self._index += 1
            elif self._cycle:
                self._index = 0
            return current


def step() -> SequenceStep:
    return SequenceStep()
