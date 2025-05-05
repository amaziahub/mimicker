import logging
import os

from colorlog import ColoredFormatter

_logger: logging.Logger | None = None


def configure_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger("mimicker")
    _logger.propagate = False
    _logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[MIMICKER] [%(asctime)s] %(levelname)s: %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(set_log_level())

    return _logger


def set_log_level():
    log_level_str = os.getenv("MIMICKER_LOG_LEVEL", "INFO").upper()
    return getattr(logging, log_level_str, logging.INFO)


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        return configure_logger()
    return _logger
