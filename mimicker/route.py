import re
from typing import Dict, Tuple, Any, Callable, Optional, Pattern, Union, List


class Route:
    """
    Represents an HTTP route with configurable response properties.
    """

    def __init__(self, method: str, path: str):
        """
        Initializes a new Route.

        Args:
            method (str): The HTTP method (GET, POST, PUT, DELETE, etc.).
            path (str): The URL path for the route, supporting parameterized paths.
        """
        self.method = method
        self.path = path
        self._body = {}
        self._delay = 0.
        self._status = 200
        self._headers: List[Tuple[str, str]] = []
        self._response_func: Optional[Callable[[], Tuple[int, Any]]] = None

        escaped_path = re.escape(path)
        parameterized_path = re.sub(r'\\{(\w+)\\}',
                                    r'(?P<\1>[^/]+)', escaped_path)
        self._compiled_path: Pattern = re.compile(f"^{parameterized_path}$")

    def delay(self, delay: float):
        """
        Sets the delay (in seconds) before returning the response.

        Args:
            delay (float): The delay time in seconds.

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._delay = delay
        return self

    def body(self, response: Union[Dict[str, Any], str] = None):
        """
        Sets the response body for the route.

        Args:
            response (Union[Dict[str, Any], str], optional): The response body (JSON or string).
            Defaults to an empty string.

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._body = response if response is not None else ""
        return self

    def status(self, status_code: int):
        """
        Sets the HTTP status code for the response.

        Args:
            status_code (int): The HTTP status code (e.g., 200, 404, 500).

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._status = status_code
        return self

    def headers(self, headers: List[Tuple[str, str]]):
        """
        Sets the HTTP headers for the response.

        Args:
            headers (List[Tuple[str, str]]): A list of key-value pairs representing headers.

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._headers = headers
        return self

    def response_func(self, func: Callable[[], Tuple[int, Any]]):
        """
        Sets a custom response function for dynamic responses.

        Args:
            func (Callable[[], Tuple[int, Any]]): A function returning a tuple (status_code, response_body).

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._response_func = func
        return self

    def build(self):
        """
        Builds the route configuration dictionary.

        Returns:
            Dict[str, Any]: The route configuration containing method, path, response settings, and handlers.
        """
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
