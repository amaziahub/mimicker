import atexit
import logging
import socketserver
import threading

from mimicker.handler import MimickerHandler
from mimicker.request_log import RequestLog
from mimicker.route import Route
from mimicker.stub_group import StubGroup


class MimickerServer:
    def __init__(self, port: int = 8080):
        self.stub_matcher = StubGroup()
        self.request_logs = {}
        self.server = socketserver.TCPServer(("", port), self._handler_factory)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        atexit.register(self.shutdown)

    def _handler_factory(self, *args):
        return MimickerHandler(self.stub_matcher, self.request_logs, *args)

    def routes(self, *routes: Route):
        for route in routes:
            route_config = route.build()
            self.stub_matcher.add(
                method=route_config["method"],
                pattern=route_config["compiled_path"],
                status_code=route_config["status"],
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
        html_report = RequestLog.generate_html_report(self.request_logs)
        with open("request_log_report.html", "w") as f:
            f.write(html_report)
        self.server.shutdown()
        if self._thread.is_alive():
            self._thread.join()
