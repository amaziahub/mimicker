import pytest

from mimicker.mimicker import mimicker


@pytest.fixture(scope="session")
def mimicker_server():
    server = mimicker(port=8080)

    yield server

    server.shutdown()
