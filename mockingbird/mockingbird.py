import atexit
import http.server
import json
import logging
import socketserver
import threading
from typing import Dict, Tuple, Any, Callable, Optional

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
    def __init__(self, port: int = 8080):
        self.stubs: Dict[str, Dict[str, Tuple[int, Any, Optional[Callable[[], Tuple[int, Any]]]]]] = {
            "GET": {},
            "POST": {},
            "PUT": {},
            "DELETE": {}
        }
        self.server = socketserver.TCPServer(("", port), self._handler_factory)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        atexit.register(self.shutdown)

    def _handler_factory(self, *args):
        handler = MockingbirdHandler
        handler.stubs = self.stubs
        return handler(*args)

    def routes(self, *routes: Route):
        for route in routes:
            route_config = route.build()
            method = route_config["method"]
            path = route_config["path"]
            self.stubs[method][path] = (
                route_config["status"],
                route_config["body"],
                route_config["response_func"]
            )
        return self

    def start(self):
        logging.info("MockingbirdServer starting on port %s", self.server.server_address[1])
        self._thread.start()
        return self

    def shutdown(self):
        self.server.shutdown()
        if self._thread.is_alive():
            self._thread.join()


def mockingbird(port: int = 8080) -> MockingbirdServer:
    server = MockingbirdServer(port).start()
    return server

