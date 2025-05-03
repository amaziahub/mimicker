import http.server
import json
from time import sleep
from typing import Any, Tuple, Optional, Dict, List
from urllib.parse import urlparse, parse_qs

from mimicker.stub_group import Stub, StubGroup


class MimickerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, stub_matcher: StubGroup, *args, **kwargs):
        self.stub_matcher = stub_matcher
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def do_PATCH(self):
        self._handle_request("PATCH")

    def _handle_request(self, method: str):
        request_headers = {key.lower(): value for key, value in self.headers.items()}
        request_body = self._get_request_body()

        parsed_url = urlparse(self.path)
        path_only = parsed_url.path
        raw_query_params = parse_qs(parsed_url.query)
        # Simplify query params: take the first value if multiple exist for the same key
        query_params = {k: v[0] for k, v in raw_query_params.items()}

        matched_stub, path_params = self.stub_matcher.match(
            method, path_only, request_headers=request_headers
        )

        if matched_stub:
            self._send_response(matched_stub, path_params, query_params, request_body, request_headers)
        else:
            self._send_404_response(method)

    def _send_response(self, matched_stub: Stub, path_params: Dict[str, str], query_params: Dict[str, str], request_body: Any, request_headers: Dict[str, str]):
        status_code, delay, response, response_func, headers = matched_stub
        if delay > 0:
            sleep(delay)
        if response_func:
            status_code, response = response_func(payload=request_body, headers=request_headers, params=path_params, query=query_params)

        self.send_response(status_code)
        self._set_headers(headers)

        self.end_headers()
        self._write_response(response, path_params)

    def _set_headers(self, headers: Optional[List[Tuple[str, str]]]):
        if headers:
            for header_name, header_value in headers:
                self.send_header(header_name, header_value)
            if not any(header[0].lower() == 'content-type' for header in headers):
                self.send_header('Content-Type', 'application/json')
        else:
            self.send_header('Content-Type', 'application/json')

    def _write_response(self, response: Any, path_params: Dict[str, str]):
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

    def _get_request_body(self) -> Optional[dict]:
        content_length = self.headers.get('content-length')
        if content_length:
            try:
                length = int(content_length)
                body = self.rfile.read(length).decode('utf-8')
                return json.loads(body) if body else None
            except (ValueError, json.JSONDecodeError):
                return None
        return None