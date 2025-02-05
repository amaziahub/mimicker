import logging
from mimicker.route import Route
from mimicker.server import MimickerServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def create_route(method: str, path: str) -> Route:
    """
    Create a route for the specified HTTP method and path.

    Args:
        method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        path (str): The path for the route.

    Returns:
        Route: The created route.
    """
    logging.info(f"Creating {method} route for path: {path}")
    return Route(method, path)

def mimicker(port: int = 8080) -> MimickerServer:
    """
    Start the Mimicker server on the specified port.

    Args:
        port (int, optional): The port to start the server on. Defaults to 8080.

    Returns:
        MimickerServer: The started Mimicker server instance.
    """
    logging.info(f"Starting Mimicker server on port: {port}")
    server = MimickerServer(port).start()
    return server

