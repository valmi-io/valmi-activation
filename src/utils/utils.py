from typing import Any
from tenacity import after_log, retry, stop_after_attempt, wait_exponential
import logging
import sys
from vyperconfig import v

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
