from hamcrest import assert_that, is_


def test_default_port(mimicker_server):
    assert_that(mimicker_server.get_port(), is_(8080))
