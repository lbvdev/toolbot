import logging

logger = logging.getLogger(__name__)


def error_log(e: Exception, desc: str | None = None):
    msg = desc or "Error"
    logger.exception("%s: %s", msg, e)
