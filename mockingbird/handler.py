import http.server
import json
from typing import Any, Tuple, Optional, Dict, Callable

from mockingbird.stub_matcher import StubMatcher


class MockingbirdHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, stub_matcher: StubMatcher, *args, **kwargs):
        self.stub_matcher = stub_matcher  # Assign the injected StubMatcher
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def _handle_request(self, method: str):
        matched_stub, path_params = self.stub_matcher.match_stub(method, self.path)

        if matched_stub:
            self._send_response(matched_stub, path_params)
        else:
            self._send_404_response(method)

    def _send_response(self, matched_stub: Tuple[int, Any, Optional[Callable]], path_params: Dict[str, str]):
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
