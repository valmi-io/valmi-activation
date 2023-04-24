from typing import Any

from airbyte_cdk import AirbyteLogger
from tenacity import retry, stop_after_attempt, wait_exponential
import functools

logger = AirbyteLogger()

max_tries = 3
min_retry_interval = 5
max_retry_interval = 60


def log_it(retry_state):
    logger.debug(str(retry_state))
    pass


def retry_on_exception(func: Any) -> Any:
    @functools.wraps(func)  # type: ignore
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=min_retry_interval, max=max_retry_interval),
        after=log_it,
        stop=stop_after_attempt(max_tries),
    )  # type: ignore
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)

    return wrapper
