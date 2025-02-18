import json

from hamcrest import assert_that, is_, has_entry, equal_to

from mimicker.mimicker import post
from tests.support.client import Client


def test_post_404(mimicker_server):
    mimicker_server.routes(
        post("/submit")
    )
    resp = Client().post_as_json('/not-found')
    assert_that(resp.status_code, is_(404))


def test_post_default_200_status_code(mimicker_server):
    mimicker_server.routes(
        post("/submit")
    )
    resp = Client().post_as_json('/submit')
    assert_that(resp.status_code, is_(200))


def test_post_picked_status_code(mimicker_server):
    mimicker_server.routes(
        post("/submit").
        status(201)
    )
    resp = Client().post_as_json('/submit')
    assert_that(resp.status_code, is_(201))


def test_post_body_as_text(mimicker_server):
    mimicker_server.routes(
        post('/submit').
        body("submission successful")
    )
    resp = Client().post_as_text('/submit', body="submission successful")
    assert_that(resp.text, is_("submission successful"))


def test_post_body_as_json(mimicker_server):
    body = {"result": "created"}
    mimicker_server.routes(
        post("/submit").
        body(body).
        status(201)
    )
    resp = Client().post_as_json('/submit', body=body)
    assert_that(resp.headers, has_entry("Content-Type", "application/json"))
    assert_that(resp.json(), equal_to(body))


def test_post_reuse_request_body(mimicker_server):
    def response_func(**kwargs):
        payload = kwargs.get("payload")
        return 202, {"my_counter": 1 + payload.get('counter')}

    body = {"counter": 1}
    mimicker_server.routes(
        post("/bump_counter").response_func(response_func)
    )
    resp = Client().post_as_json('/bump_counter', body=body)
    assert_that(resp.status_code, equal_to(202))
    assert_that(resp.json(), equal_to({"my_counter": 2}))


def test_post_empty_response(mimicker_server):
    mimicker_server.routes(
        post("/clear").
        body(None).
        status(204)
    )
    resp = Client().post_as_json('/clear')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))


def test_post_body_with_text_content(mimicker_server):
    body = "This is a plain text submission."
    mimicker_server.routes(
        post("/submit-text").
        body(body).
        status(200)
    )
    resp = Client().post_as_text('/submit-text', body=body)
    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_(body))


def test_post_body_with_json_content(mimicker_server):
    body = {"message": "Data submitted"}
    mimicker_server.routes(
        post("/submit-json").
        body(body).
        status(201)
    )
    resp = Client().post_as_json('/submit-json', body=body)
    assert_that(resp.status_code, is_(201))
    assert_that(resp.json(), equal_to(body))


def test_post_file_upload(mimicker_server):
    file_content = b"Test file content"
    mimicker_server.routes(
        post("/upload").
        body("File uploaded successfully").
        status(200)
    )
    with open('/tmp/test_file.txt', 'wb') as f:
        f.write(file_content)

    with open('/tmp/test_file.txt', 'rb') as file:
        resp = Client().post_as_file('/upload', body={'file': file})

    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_("File uploaded successfully"))
