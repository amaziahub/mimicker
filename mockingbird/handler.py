import http.server
import json
from re import Pattern
from typing import Dict, Tuple, Any, Optional, Callable


class MockingbirdHandler(http.server.SimpleHTTPRequestHandler):
    stubs: Dict[str, Dict[
        Pattern,
        Tuple[int, Any, Optional[Callable[[], Tuple[int, Any]]]]
    ]] = {}

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def _handle_request(self, method: str):
        matched_stub, path_params = self._match_stub(method)

        if matched_stub:
            self._send_response(matched_stub, path_params)
        else:
            self._send_404_response(method)

    def _match_stub(self, method: str):
        matched_stub = None
        path_params = {}

        # Match the request path against the compiled regex patterns in stubs
        for compiled_path, (status_code, response, response_func) in\
                self.stubs[method].items():
            match = compiled_path.match(self.path)
            if match:
                matched_stub = (status_code, response, response_func)
                path_params = match.groupdict()  # Extract path parameters
                break

        return matched_stub, path_params

    def _send_response(self, matched_stub, path_params):
        status_code, response, response_func = matched_stub
        if response_func:
            status_code, response = response_func()

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if isinstance(response, dict):
            response = self._format_response(response, path_params)
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif isinstance(response, str):
            self.wfile.write(response.encode('utf-8'))
        else:
            self.wfile.write(str(response).encode('utf-8'))

    def _send_404_response(self, method: str):
        self.send_response(404)
        self.end_headers()
        self.log_message("Responded with 404 for %s request to %s", method, self.path)

    @staticmethod
    def _format_response(response: dict, path_params: dict):
        return {k: (v.format(**path_params) if isinstance(v, str) else v)
                for k, v in response.items()}
