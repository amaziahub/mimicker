import re
from typing import Pattern, Dict, Tuple, Any, Optional, Callable


class StubMatcher:
    def __init__(self):
        self.stubs: Dict[str, Dict[Pattern, Tuple[int, Any, Optional[Callable[[], Tuple[int, Any]]]]]] = {}

    def add_stub(self, method: str, pattern: str, status_code: int, response: Any, response_func: Optional[Callable[[], Tuple[int, Any]]] = None):
        if method not in self.stubs:
            self.stubs[method] = {}
        self.stubs[method][re.compile(pattern)] = (status_code, response, response_func)

    def match_stub(self, method: str, path: str):
        matched_stub = None
        path_params = {}

        for compiled_path, (status_code, response, response_func) in self.stubs.get(method, {}).items():
            match = compiled_path.match(path)
            if match:
                matched_stub = (status_code, response, response_func)
                path_params = match.groupdict()
                break

        return matched_stub, path_params
