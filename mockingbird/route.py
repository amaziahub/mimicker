from typing import Dict, Any


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
