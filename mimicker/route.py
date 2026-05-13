import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union

from mimicker.rate_limit import RateLimitConfig
from mimicker.regex import parse_endpoint_pattern


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
        self._response_func: Optional[Callable[..., Tuple[int, Any]]] = None
        self._compiled_path: Pattern = parse_endpoint_pattern(path)
        self._rate_limit: Optional[RateLimitConfig] = None

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

    def response_func(self, func: Callable[..., Tuple[int, Any]]):
        """
        Sets a custom response function for dynamic responses.

        Args:
            func (Callable[..., Tuple[int, Any]]): A function that returns (status_code, response_body).

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._response_func = func
        return self

    def rate_limit(
        self,
        max_requests: int = 10,
        window_seconds: float = 60.0,
        key_header: Optional[str] = None,
        status_code: int = 429,
        body: Any = None,
        headers: Optional[List[Tuple[str, str]]] = None,
    ):
        """
        Configures rate limiting for this route.

        Args:
            max_requests: Maximum number of requests allowed within the window.
            window_seconds: Time window in seconds.
            key_header: Optional request header to key rate limits by (e.g. "X-Api-Key").
            status_code: HTTP status code to return when rate limited.
            body: Response body when rate limited.
            headers: Response headers when rate limited.

        Returns:
            Route: The current Route instance (for method chaining).
        """
        self._rate_limit = RateLimitConfig(
            max_requests=max_requests,
            window_seconds=window_seconds,
            key_header=key_header,
            status_code=status_code,
            body=body if body is not None else {"error": "Too Many Requests"},
            headers=headers or [("Retry-After", str(int(window_seconds))),
                                ("Content-Type", "application/json")],
        )
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
            "response_func": self._response_func,
            "rate_limit": self._rate_limit,
        }
