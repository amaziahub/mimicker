import pytest
import threading

from mockingbird.mockingbird import mockingbird


@pytest.fixture(scope="session")
def mockingbird_server():
    server = mockingbird(port=8080)

    yield server

    server.shutdown()
