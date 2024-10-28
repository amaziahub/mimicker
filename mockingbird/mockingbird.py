import logging
import socketserver
import threading
from typing import Dict, Tuple, Any

from mockingbird.handler import MockingbirdHandler
from mockingbird.route import Route

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


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


def mockingbird(port: int) -> MockingbirdServer:
    return MockingbirdServer(port)
