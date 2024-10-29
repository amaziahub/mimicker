import logging

from mockingbird.route import Route
from mockingbird.server import MockingbirdServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def get(path: str) -> Route:
    return Route("GET", path)


def post(path: str) -> Route:
    return Route("POST", path)


def put(path: str) -> Route:
    return Route("PUT", path)


def delete(path: str) -> Route:
    return Route("DELETE", path)


def mockingbird(port: int = 8080) -> MockingbirdServer:
    server = MockingbirdServer(port).start()
    return server
