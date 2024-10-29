import http.server
import json
import logging
from typing import Dict, Tuple, Any, Optional, Callable


class MockingbirdHandler(http.server.SimpleHTTPRequestHandler):
    stubs: Dict[str, Dict[str, Tuple[int, Any, Optional[Callable[[], Tuple[int, Any]]]]]] = {}

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def _handle_request(self, method: str):
        if self.path in self.stubs[method]:
            status_code, response, response_func = self.stubs[method][self.path]
            if response_func:
                # If a response function is defined, call it to get status and response
                status_code, response = response_func()

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            if isinstance(response, dict):
                self.wfile.write(json.dumps(response).encode('utf-8'))
            elif isinstance(response, str):
                self.wfile.write(response.encode('utf-8'))
            elif isinstance(response, bytes):
                self.wfile.write(response)
            else:
                self.wfile.write(str(response).encode('utf-8'))

            self.log_message("Responded with %d for %s request to %s", status_code, method, self.path)
        else:
            self.send_response(404)
            self.end_headers()
            self.log_message("Responded with 404 for %s request to %s", method, self.path)

    def log_message(self, format: str, *args):
        logging.info("%s - %s" % (self.address_string(), format % args))