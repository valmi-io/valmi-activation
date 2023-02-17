"""docs:  http://127.0.0.1:8000/docs"""
import functools
import logging
import logging.config
import sys
from typing import Any

import uvicorn
from tenacity import after_log, retry, stop_after_attempt, wait_exponential
from vyper import v

from app import create_app
from vyperconfig import setup_vyper

# Logging init
logger = logging.getLogger(v.get("LOGGER_NAME"))


def retry_wrapper(func: Any) -> Any:
    @functools.wraps(func)  # type: ignore
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=1, max=10),
        after=after_log(logger, logging.WARN),
        stop=stop_after_attempt(2),
    )  # type: ignore
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)

    return wrapper


def fail_handler(func: Any) -> Any:
    @functools.wraps(func)  # type: ignore
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                "Faileure %s due to error: %s",
                str(func.__name__),
                str(e),
            )
            sys.exit(1)

    return wrapper


def main() -> None:
    uvicorn.run(app())


def app():
    setup_vyper()
    logging.config.dictConfig(v.get("LOGGING_CONF"))
    logger.info("Starting server...")
    return create_app()


if __name__ == "__main__":
    main()
