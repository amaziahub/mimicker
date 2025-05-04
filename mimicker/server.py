import atexit
import socketserver
import threading

from logger import get_logger
from mimicker.handler import MimickerHandler
from mimicker.route import Route
from mimicker.stub_group import StubGroup


class ReusableAddressThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class MimickerServer:
    """
    A lightweight HTTP mocking server.

    This server allows defining request-response routes for testing or simulation purposes.
    """
    def __init__(self, port: int = 8080):
        """
        Initializes the Mimicker server.

        Args:
            port (int, optional): The port to run the server on. Defaults to 8080.
        """
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
                response_func=route_config["response_func"]
            )
        return self

    def start(self):
        """
        Starts the Mimicker server in a background thread.

        Returns:
            MimickerServer: The current server instance (for method chaining).
        """
        self.logger.info("🚀 MimickerServer started and listening on port %s",
                         self.server.server_address[1])
        self._thread.start()
        return self

    def shutdown(self):
        """
        Shuts down the Mimicker server gracefully.

        Ensures that the server is stopped and the thread is joined if still running.
        """
        self.server.server_close()
        self.server.shutdown()
        if self._thread.is_alive():
            self._thread.join()
