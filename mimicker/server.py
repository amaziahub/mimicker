import atexit
import socketserver
import threading

from mimicker.logger import get_logger
from mimicker.handler import MimickerHandler
from mimicker.route import Route
from mimicker.stub_group import StubGroup
from mimicker.tracking import RequestTracker


class ReusableAddressThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    # Default backlog of 5 causes RST on macOS when more than 5 connections
    # arrive simultaneously before the first accept() clears the queue.
    request_queue_size = 128


class MimickerServer:
    """
    A lightweight HTTP mocking server.

    This server allows defining request-response routes for testing or simulation purposes.
    """
    def __init__(self, port: int = 8080):
        self.logger = get_logger()
        self.stub_matcher = StubGroup()
        self.server = ReusableAddressThreadingTCPServer(("", port), self._handler_factory)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        atexit.register(self.shutdown)
        self.logger.debug("Initialized MimickerServer on port %s", port)

    def _handler_factory(self, *args):
        self.logger.debug("Creating a new handler for incoming connection")
        return MimickerHandler(self.stub_matcher, *args)

    def routes(self, *routes: Route):
        """
        Adds multiple routes to the server.

        Args:
            *routes (Route): One or more Route instances to be added.

        Returns:
            MimickerServer: The current server instance (for method chaining).
        """
        for route in routes:
            route_config = route.build()
            self.stub_matcher.add(
                method=route_config["method"],
                pattern=route_config["compiled_path"],
                status_code=route_config["status"],
                delay=route_config["delay"],
                response=route_config["body"],
                headers=route_config["headers"],
                response_func=route_config["response_func"],
                rate_limit=route_config["rate_limit"],
                sequence=route_config["sequence"],
                path_template=route_config["path"],
            )
        return self

    def load_config(self, path: str) -> "MimickerServer":
        """
        Load routes from a YAML or JSON stub config file.

        Args:
            path (str): Path to the config file.

        Returns:
            MimickerServer: The current server instance (for method chaining).
        """
        from mimicker.config import build_routes, load_config, validate_config
        data = load_config(path)
        errors = validate_config(data)
        if errors:
            raise ValueError(f"Invalid config file '{path}': {'; '.join(errors)}")
        return self.routes(*build_routes(data))

    @property
    def tracker(self) -> RequestTracker:
        return self.stub_matcher.tracker

    def get_port(self) -> int:
        """
        Returns the port number the Mimicker server is listening on.

        Returns:
            int: The port number.
        """
        return self.server.server_address[1]

    def start(self):
        """
        Starts the Mimicker server in a background thread.

        Returns:
            MimickerServer: The current server instance (for method chaining).
        """
        self.logger.info("MimickerServer started and listening on port %s",
                         self.server.server_address[1])
        self._thread.start()
        return self

    def shutdown(self):
        """
        Shuts down the Mimicker server gracefully.
        """
        self.server.shutdown()
        self.server.server_close()
        if self._thread.is_alive():
            self._thread.join()
