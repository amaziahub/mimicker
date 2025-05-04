import logging
from io import StringIO

from hamcrest import assert_that, contains_string

from logger import configure_logger


def test_logger_outputs(caplog):
    logger = configure_logger()
    logger.addHandler(caplog.handler)

    with caplog.at_level(logging.INFO):
        logger.info("hello mimicker")

    assert_that(caplog.text, contains_string("hello mimicker"))


def test_logger_output_includes_prefix():
    buffer = StringIO()

    logger = configure_logger()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logger.handlers[0].formatter)
    logger.addHandler(handler)

    logger.info("format test message")
    handler.flush()

    output = buffer.getvalue()
    assert_that(output, contains_string("[MIMICKER]"))
    assert_that(output, contains_string("format test message"))

    logger.removeHandler(handler)
