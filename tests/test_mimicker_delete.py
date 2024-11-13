from hamcrest import assert_that, is_

from mimicker.mimicker import delete
from tests.support.client import Client


def test_delete_404(mimicker_server):
    mimicker_server.routes(
        delete("/remove")
    )
    resp = Client().delete('/not-found')
    assert_that(resp.status_code, is_(404))


def test_delete_default_200_status_code(mimicker_server):
    mimicker_server.routes(
        delete("/remove")
    )
    resp = Client().delete('/remove')
    assert_that(resp.status_code, is_(200))


def test_delete_picked_status_code(mimicker_server):
    mimicker_server.routes(
        delete("/remove").
        status(204)
    )
    resp = Client().delete('/remove')
    assert_that(resp.status_code, is_(204))


def test_delete_empty_response(mimicker_server):
    mimicker_server.routes(
        delete("/remove").
        body(None).
        status(204)
    )
    resp = Client().delete('/remove')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))
