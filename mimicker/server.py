import atexit
import logging
import socketserver
import threading

from mimicker.handler import MimickerHandler
from mimicker.route import Route
from mimicker.stub_group import StubGroup

class ReusableAddressTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class MimickerServer:
    def __init__(self, port: int = 8080):
        self.stub_matcher = StubGroup()
        self.server = ReusableAddressTCPServer(("", port), self._handler_factory)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        atexit.register(self.shutdown)

    def _handler_factory(self, *args):
        return MimickerHandler(self.stub_matcher, *args)

    def routes(self, *routes: Route):
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
        logging.info("MimickerServer starting on port %s",
                     self.server.server_address[1])
        self._thread.start()
        return self

    def shutdown(self):
        self.server.shutdown()
        if self._thread.is_alive():
            self._thread.join()
