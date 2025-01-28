import atexit
import logging
import socketserver
import threading

from mimicker.handler import MimickerHandler
from mimicker.report_generator import ReportGenerator
from mimicker.request_log import RequestLog
from mimicker.route import Route
from mimicker.stub_group import StubGroup


def dump_report(raw_data, path="mimicker_log_report.html"):
    with open(path, "w") as f:
        f.write(raw_data)


class MimickerServer:
    def __init__(self, port: int = 8080):
        self.report_generator = None
        self.report_format = None
        self.report_path = None
        self.reporting_enabled = False
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

    def enable_reporting(self, format="html", path="report.html"):
        self.reporting_enabled = True
        self.report_format = format
        self.report_path = path
        self.report_generator = ReportGenerator(format, path)
        return self

    def start(self):
        logging.info("MimickerServer starting on port %s",
                     self.server.server_address[1])
        self._thread.start()
        return self

    def shutdown(self):
        if self.enable_reporting:
            dump_report(self.report_generator.generate(self.request_logs), self.report_path)
        self.server.shutdown()
        if self._thread.is_alive():
            self._thread.join()
