import os

import pytest

from mimicker.mimicker import mimicker


@pytest.fixture(scope="session")
def mimicker_server():
    server = mimicker(port=8080)

    yield server

    server.shutdown()


@pytest.fixture
def cleanup_reports(request):
    def cleanup():
        for file_path in ["/tmp/report.html", "/tmp/report.json", "/tmp/report.md"]:
            if os.path.exists(file_path):
                os.remove(file_path)
    request.addfinalizer(cleanup)
