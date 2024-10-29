import atexit
import logging
import socketserver
import threading
from re import Pattern
from typing import Dict, Tuple, Any, Optional, Callable

from mockingbird.handler import MockingbirdHandler
from mockingbird.route import Route


class MockingbirdServer:
    def __init__(self, port: int = 8080):
        self.stubs: Dict[str, Dict[
            Pattern,
            Tuple[int, Any, Optional[Callable[[], Tuple[int, Any]]]]]] = {
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
            compiled_path = route_config["compiled_path"]
            self.stubs[method][compiled_path] = (
                route_config["status"],
                route_config["body"],
                route_config["response_func"]
            )
        return self

    def start(self):
        logging.info("MockingbirdServer starting on port %s",
                     self.server.server_address[1])
        self._thread.start()
        return self

    def shutdown(self):
        self.server.shutdown()
        if self._thread.is_alive():
            self._thread.join()
