import re

from typing import Dict, Tuple, Any, Callable, Optional, Pattern, Union, List


class Route:
    def __init__(self, method: str, path: str):
        self.method = method
        self.path = path
        self._body = {}
        self._delay = 0
        self._status = 200
        self._headers: List[Tuple[str, str]] = []
        self._response_func: Optional[Callable[[], Tuple[int, Any]]] = None

        escaped_path = re.escape(path)
        parameterized_path = re.sub(r'\\{(\w+)\\}',
                                    r'(?P<\1>[^/]+)', escaped_path)
        self._compiled_path: Pattern = re.compile(f"^{parameterized_path}$")

    def delay(self, delay: float):
        """
        Sets the delay (in seconds) to wait before returning the response
        """
        self._delay = delay
        return self

    def body(self, response: Union[Dict[str, Any], str] = None):
        self._body = response if response is not None else ""
        return self

    def status(self, status_code: int):
        self._status = status_code
        return self

    def headers(self, headers: List[Tuple[str, str]]):
        self._headers = headers
        return self

    def response_func(self, func: Callable[[], Tuple[int, Any]]):
        self._response_func = func
        return self

    def build(self):
        return {
            "method": self.method,
            "path": self.path,
            "compiled_path": self._compiled_path,
            "delay": self._delay,
            "body": self._body,
            "status": self._status,
            "headers": self._headers,
            "response_func": self._response_func
        }
