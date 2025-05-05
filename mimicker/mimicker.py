from mimicker.route import Route
from mimicker.server import MimickerServer


def get(path: str) -> Route:
    """
    Creates a GET route for the specified path.

    Args:
        path (str): The URL path for the route.

    Returns:
        Route: A GET route instance.
    """
    return Route("GET", path)


def post(path: str) -> Route:
    """
    Creates a POST route for the specified path.

    Args:
        path (str): The URL path for the route.

    Returns:
        Route: A POST route instance.
    """
    return Route("POST", path)


def put(path: str) -> Route:
    """
    Creates a PUT route for the specified path.

    Args:
        path (str): The URL path for the route.

    Returns:
        Route: A PUT route instance.
    """
    return Route("PUT", path)


def delete(path: str) -> Route:
    """
    Creates a DELETE route for the specified path.

    Args:
        path (str): The URL path for the route.

    Returns:
        Route: A DELETE route instance.
    """
    return Route("DELETE", path)


def patch(path: str) -> Route:
    """
    Creates a PATCH route for the specified path.

    Args:
        path (str): The URL path for the route.

    Returns:
        Route: A PATCH route instance.
    """
    return Route("PATCH", path)


def mimicker(port: int = 8080) -> MimickerServer:
    """
    Starts a Mimicker server on the specified port.

    Args:
        port (int, optional): The port to run the server on. Defaults to 8080.

    Returns:
        MimickerServer: An instance of the running Mimicker server.
    """
    server = MimickerServer(port).start()
    return server
