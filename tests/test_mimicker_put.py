from hamcrest import assert_that, is_, has_entry, equal_to

from mimicker.mimicker import put
from tests.support.client import Client


def test_put_404(mimicker_server):
    mimicker_server.routes(
        put("/update")
    )
    resp = Client().put('/not-found')
    assert_that(resp.status_code, is_(404))


def test_put_default_200_status_code(mimicker_server):
    mimicker_server.routes(
        put("/update")
    )
    resp = Client().put('/update')
    assert_that(resp.status_code, is_(200))


def test_put_picked_status_code(mimicker_server):
    mimicker_server.routes(
        put("/update").
        status(202)
    )
    resp = Client().put('/update')
    assert_that(resp.status_code, is_(202))


def test_put_body_as_text(mimicker_server):
    mimicker_server.routes(
        put('/update').
        body("update successful")
    )
    resp = Client().put_as_text('/update', body="update successful")
    assert_that(resp.text, is_("update successful"))


def test_put_body_as_json(mimicker_server):
    body = {"result": "updated"}
    mimicker_server.routes(
        put("/update").
        body(body).
        status(200)
    )
    resp = Client().put_as_json('/update', body=body)
    assert_that(resp.headers, has_entry("Content-Type", "application/json"))
    assert_that(resp.json(), equal_to(body))


def test_put_empty_response(mimicker_server):
    mimicker_server.routes(
        put("/clear").
        body(None).
        status(204)
    )
    resp = Client().put('/clear')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))


def test_put_text_content(mimicker_server):
    body = "This is an update with plain text."
    mimicker_server.routes(
        put("/update-text").
        body(body).
        status(200)
    )
    resp = Client().put_as_text('/update-text', body=body)
    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_(body))


def test_put_json_content(mimicker_server):
    body = {"message": "Updated successfully"}
    mimicker_server.routes(
        put("/update-json").
        body(body).
        status(200)
    )
    resp = Client().put_as_json('/update-json', body=body)
    assert_that(resp.status_code, is_(200))
    assert_that(resp.json(), equal_to(body))
