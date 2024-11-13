import logging

from mimicker.route import Route
from mimicker.server import MimickerServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def get(path: str) -> Route:
    return Route("GET", path)


def post(path: str) -> Route:
    return Route("POST", path)


def put(path: str) -> Route:
    return Route("PUT", path)


def delete(path: str) -> Route:
    return Route("DELETE", path)


def mimicker(port: int = 8080) -> MimickerServer:
    server = MimickerServer(port).start()
    return server
