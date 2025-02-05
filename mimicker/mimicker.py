import logging
from mimicker.route import Route
from mimicker.server import MimickerServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def get(path: str) -> Route:
    """
    Create a GET route for the given path.
    """
    logging.info(f"Creating GET route for path: {path}")
    return Route("GET", path)


def post(path: str) -> Route:
    """
    Create a POST route for the given path.
    """
    logging.info(f"Creating POST route for path: {path}")
    return Route("POST", path)


def put(path: str) -> Route:
    """
    Create a PUT route for the given path.
    """
    logging.info(f"Creating PUT route for path: {path}")
    return Route("PUT", path)


def delete(path: str) -> Route:
    """
    Create a DELETE route for the given path.
    """
    logging.info(f"Creating DELETE route for path: {path}")
    return Route("DELETE", path)


def mimicker(port: int = 8080) -> MimickerServer:
    """
    Start the Mimicker server on the specified port.
    """
    logging.info(f"Starting Mimicker server on port: {port}")
    server = MimickerServer(port).start()
    return server
