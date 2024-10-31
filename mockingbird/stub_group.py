import re
from typing import Pattern, Dict, Tuple, Any, Optional, Callable, Union


class StubGroup:
    def __init__(self):
        self.stubs: Dict[
            str,
            Dict[
                Pattern,
                Tuple[int, Any, Optional[
                    Callable[[], Tuple[int, Any]]]
                ]]] = {}

    def add(self, method: str,
            pattern: Union[str, Pattern], status_code: int, response: Any,
            response_func: Optional[Callable[[], Tuple[int, Any]]] = None):
        if method not in self.stubs:
            self.stubs[method] = {}

        if isinstance(pattern, str):
            pattern = re.compile(f"^{re.sub(r'\\{(\\w+)\\}',
                                            r'(?P<\\1>[^/]+)', pattern)}$")

        self.stubs[method][pattern] = (status_code, response, response_func)

    def match(self, method: str, path: str):
        matched_stub = None
        path_params = {}

        for compiled_path, (status_code, response, response_func)\
                in self.stubs.get(method, {}).items():
            match = compiled_path.match(path)
            if match:
                matched_stub = (status_code, response, response_func)
                path_params = match.groupdict()
                break

        return matched_stub, path_params
