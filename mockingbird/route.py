import re

from typing import Dict, Tuple, Any, Callable, Optional, Pattern


class Route:
    def __init__(self, method: str, path: str):
        self.method = method
        self.path = path
        self._body = {}
        self._status = 200
        self._response_func: Optional[Callable[[], Tuple[int, Any]]] = None

        escaped_path = re.escape(path)
        parameterized_path = re.sub(r'\\{(\w+)\\}',
                                    r'(?P<\1>[^/]+)', escaped_path)
        self._compiled_path: Pattern = re.compile(f"^{parameterized_path}$")

    def body(self, response: Dict[str, Any]):
        self._body = response
        return self

    def status(self, status_code: int):
        self._status = status_code
        return self

    def response_func(self, func: Callable[[], Tuple[int, Any]]):
        self._response_func = func
        return self

    def build(self):
        return {
            "method": self.method,
            "path": self.path,
            "compiled_path": self._compiled_path,
            "body": self._body,
            "status": self._status,
            "response_func": self._response_func
        }
