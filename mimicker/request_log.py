import json
from datetime import datetime


class RequestLog:
    def __init__(self, method, path, timestamp, body):
        self.method = method
        self.path = path
        self.timestamp = timestamp
        self.body = body

    @staticmethod
    def log_request(request_logs, method, path, body):
        """Log requests to the server."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if path not in request_logs:
            request_logs[path] = []
        request_logs[path].append(RequestLog(method, path, timestamp, body))
