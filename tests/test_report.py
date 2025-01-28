import os

from hamcrest import assert_that, is_, contains_string

from mimicker.mimicker import post
from tests.support.client import Client


def test_generate_html_report(mimicker_server):
    report_path = "/tmp/report.html"
    mimicker_server.enable_reporting(format="html", path=report_path)
    mimicker_server.routes(
        post("/submit").
        body({"result": "success"}).
        status(201)
    )

    Client().post_as_json('/submit', body={"key": "value"})

    # Assert that the report file exists
    assert_that(os.path.exists(report_path), is_(True))

    # Assert that the content contains valid HTML structure
    with open(report_path, "r") as report_file:
        content = report_file.read()
        assert_that(content, contains_string("<html>"))
        assert_that(content, contains_string("success"))