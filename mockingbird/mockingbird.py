import http.server
import socketserver
import json
import logging
import threading
from typing import Dict, Tuple, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class Route:
    def __init__(self, method: str, path: str):
        self.method = method
        self.path = path
        self._body = {}
        self._status = 200

    def body(self, response: Dict[str, Any]):
        self._body = response
        return self

    def status(self, status_code: int):
        self._status = status_code
        return self

    def build(self):
        return {
            "method": self.method,
            "path": self.path,
            "body": self._body,
            "status": self._status
        }


def get(path: str) -> Route:
    return Route("GET", path)


def post(path: str) -> Route:
    return Route("POST", path)


def put(path: str) -> Route:
    return Route("PUT", path)


def delete(path: str) -> Route:
    return Route("DELETE", path)


class MockingbirdServer:
    def __init__(self, port: int):
        self.stubs: Dict[str, Dict[str, Tuple[int, Any]]] = {
            "GET": {},
            "POST": {},
            "PUT": {},
            "DELETE": {}
        }
        self.server = socketserver.TCPServer(("", port), self._handler_factory)
        self._thread = None

    def _handler_factory(self, *args):
        handler = MockingbirdHandler
        handler.stubs = self.stubs
        return handler(*args)

    def routes(self, *routes: Route):
        for route in routes:
            route_config = route.build()
            method = route_config["method"]
            path = route_config["path"]
            self.stubs[method][path] = (route_config["status"], route_config["body"])
        return self

    def start(self):
        logging.info("MockingbirdServer starting on port %s", self.server.server_address[1])
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def shutdown(self):
        logging.info("MockingbirdServer shutting down.")
        self.server.shutdown()
        if self._thread:
            self._thread.join()


class MockingbirdHandler(http.server.SimpleHTTPRequestHandler):
    stubs: Dict[str, Dict[str, Tuple[int, Any]]] = {}

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
            status_code, response = self.stubs[method][self.path]
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            self.log_message("Responded with %d for %s request to %s", status_code, method, self.path)
        else:
            self.send_response(404)
            self.end_headers()
            self.log_message("Responded with 404 for %s request to %s", method, self.path)

    def log_message(self, format: str, *args):
        logging.info("%s - %s" % (self.address_string(), format % args))


def mockingbird(port: int) -> MockingbirdServer:
    return MockingbirdServer(port)
