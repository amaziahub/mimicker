from re import Pattern
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

from mimicker.rate_limit import RateLimitConfig, RateLimitTracker
from mimicker.regex import parse_endpoint_pattern
from mimicker.sequence import SequenceConfig
from mimicker.tracking import RequestTracker


class Stub(NamedTuple):
    status_code: int
    delay: float
    response: Any
    response_func: Optional[Callable] = None
    headers: Optional[List[Tuple[str, str]]] = None
    rate_limit: Optional[RateLimitConfig] = None
    sequence: Optional[SequenceConfig] = None


class StubGroup:
    def __init__(self):
        self.stubs: Dict[str, Dict[Pattern, Stub]] = {}
        self.rate_limiter = RateLimitTracker()
        self.tracker = RequestTracker()
        self._stub_keys: Dict[int, Tuple[str, str]] = {}  # id(pattern) -> (method, path_template)

    def add(self, method: str, pattern: Union[str, Pattern],
            status_code: int, response: Any, delay: Optional[float] = 0,
            response_func: Optional[Callable[[], Tuple[int, Any]]] = None,
            headers: Optional[List[Tuple[str, str]]] = None,
            rate_limit: Optional[RateLimitConfig] = None,
            sequence: Optional[SequenceConfig] = None,
            path_template: str = ""):
        if method not in self.stubs:
            self.stubs[method] = {}

        if isinstance(pattern, str):
            path_template = path_template or pattern
            pattern = parse_endpoint_pattern(pattern)

        self.stubs[method][pattern] = Stub(status_code, delay, response, response_func,
                                           headers, rate_limit, sequence)
        self._stub_keys[id(pattern)] = (method, path_template or str(pattern))
        self.tracker.register_stub(method, path_template or str(pattern))

    def match(self, method: str, path: str,
              request_headers: Optional[Dict[str, str]] = None) -> Tuple[
            Optional[Stub], Dict[str, str]]:
        matched_stub = None
        path_params = {}
        matched_pattern = None

        for compiled_path, stub in self.stubs.get(method, {}).items():
            match = compiled_path.match(path)
            if match:
                headers_included = True
                if stub.headers and request_headers:
                    headers_included = all(
                        header_name in request_headers
                        and request_headers[header_name] == header_value
                        for header_name, header_value in stub.headers
                    )

                if stub.headers and not headers_included:
                    pass

                matched_stub = stub
                matched_pattern = compiled_path
                path_params = match.groupdict()
                break

        if matched_stub and matched_pattern is not None:
            stub_key = self._stub_keys.get(id(matched_pattern))
            if stub_key:
                self.tracker.record_hit(*stub_key)
        elif matched_stub is None:
            from urllib.parse import urlparse
            clean_path = urlparse(path).path
            # Don't count admin paths as unmatched — they're handled by the server itself.
            if not clean_path.startswith("/__mimicker__/"):
                self.tracker.record_unmatched(method, clean_path)

        return matched_stub, path_params
