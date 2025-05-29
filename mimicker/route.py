import re
from typing import Dict, Tuple, Any, Callable, Optional, Pattern, Union, List

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

        self._responses_sequence = []
        self._response_index = 0

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
        if self._responses_sequence:
            self._responses_sequence[-1][
                "body"] = response if response is not None else ""
        else:
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
        if self._responses_sequence:
            # If sequence is being used, add this response to the sequence
            self._responses_sequence.append(
                {"status": status_code, "body": self._body, "times": 1, "always": False}
            )
        else:
            # If no sequence is defined, just set the status as before
            self._status = status_code
        return self

    def times(self, times: int):
        """
        Sets how many times the last response should be returned.

        Args:
            times (int): The number of times the response should be returned.

        Returns:
            Route: The current Route instance (for method chaining).
        """
        if self._responses_sequence:
            self._responses_sequence[-1]["times"] = times
        return self

    def always(self):
        """
        Marks the last response to be repeated indefinitely.

        Returns:
            Route: The current Route instance (for method chaining).
        """
        if self._responses_sequence:
            self._responses_sequence[-1]["always"] = True
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

    def sequence(self, *response_tuples):
        """
        Defines a sequence of responses to be returned in order.

        Args:
            *response_tuples: A sequence of tuples (status_code, body, times).

        Returns:
            Route: The current Route instance (for method chaining).
        """
        for status, body, times in response_tuples:
            self._responses_sequence.append(
                {"status": status, "body": body, "times": times, "always": False}
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
            "responses_sequence": self._responses_sequence
        }

    def handle_request(self, method):
        """
        Handles the HTTP request and returns the appropriate response based on the sequence.
        """
        if self._response_index < len(self._responses_sequence):
            response = self._responses_sequence[self._response_index]
            if response["always"]:
                pass
            elif response.get("times", 1) > 1:
                response["times"] -= 1
            else:
                self._response_index += 1

            return {"status": response["status"], "body": response["body"]}

        return {"status": 404, "body": "Not Found"}
