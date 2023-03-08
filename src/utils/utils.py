from typing import Any
from tenacity import after_log, retry, stop_after_attempt, wait_exponential
import logging
import sys
from vyperconfig import v
import functools

# Logging init
logger = logging.getLogger(v.get("LOGGER_NAME"))


max_tries = int(v.get("DAGTSER_MAX_TRIES") or 10)
min_retry_interval = int(v.get("DAGSTER_MIN_RETRY_INTERVAL") or 60)
max_retry_interval = int(v.get("DAGSTER_MAX_RETRY_INTERVAL") or 300)


def retry_on_exception(func: Any) -> Any:
    @functools.wraps(func)  # type: ignore
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=min_retry_interval, max=max_retry_interval),
        after=after_log(logger, logging.WARN),
        stop=stop_after_attempt(max_tries),
    )  # type: ignore
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)

    return wrapper


def exception_to_sys_exit(func: Any) -> Any:
    @functools.wraps(func)  # type: ignore
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                "Failure %s due to error: %s",
                str(func.__name__),
                str(e),
            )
            sys.exit(1)

    return wrapper
