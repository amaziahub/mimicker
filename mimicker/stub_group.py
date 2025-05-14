from typing import Pattern, Dict, Tuple, Any, Optional, Callable, Union, List, \
    NamedTuple

from mimicker.regex import parse_endpoint_pattern


class Stub(NamedTuple):
    status_code: int
    delay: float
    response: Any
    response_func: Optional[Callable]
    headers: Optional[List[Tuple[str, str]]]


class StubGroup:
    def __init__(self):
        self.stubs: Dict[
            str,
            Dict[Pattern, Stub]
        ] = {}

    def add(self, method: str, pattern: Union[str, Pattern],
            status_code: int, response: Any, delay: Optional[float] = 0,
            response_func: Optional[Callable[[], Tuple[int, Any]]] = None,
            headers: Optional[List[Tuple[str, str]]] = None):
        if method not in self.stubs:
            self.stubs[method] = {}

        if isinstance(pattern, str):
            pattern = parse_endpoint_pattern(pattern)

        self.stubs[method][pattern] = Stub(status_code, delay, response, response_func,
                                           headers)

    def match(self, method: str, path: str,
              request_headers: Optional[Dict[str, str]] = None) -> Tuple[
        Stub, Dict[str, str]]:
        matched_stub = None
        path_params = {}

        for compiled_path, (status_code, delay, response, response_func, headers) \
                in self.stubs.get(method, {}).items():
            match = compiled_path.match(path)
            if match:
                headers_included = True
                if headers and request_headers:
                    headers_included = all(
                        header_name in request_headers
                        and request_headers[header_name] == header_value
                        for header_name, header_value in headers
                    )

                if headers and not headers_included:
                    pass

                matched_stub = Stub(status_code, delay, response, response_func,
                                    headers)
                path_params = match.groupdict()
                break

        return matched_stub, path_params
