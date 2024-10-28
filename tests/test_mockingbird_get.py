import time

import requests
from hamcrest import assert_that, is_

from mockingbird.mockingbird import mockingbird, get


def test_should_get_status_code():
    server = mockingbird(8080).routes(
        get("/hello")
        .body({"hello": "mockingbird"})
        .status(201)
    )

    server.start()

    time.sleep(1)

    response = requests.get('http://localhost:8080/hello')
    assert_that(response.status_code, is_(201))

    server.shutdown()
