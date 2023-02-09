"""docs:  http://127.0.0.1:8000/docs"""
import functools
import logging
import logging.config
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import Json
from tenacity import after_log, retry, stop_after_attempt, wait_exponential
from vyper import v

from api.ctrls import users


def setup_vyper() -> None:
    v.set_config_type("yaml")
    v.set_config_name("config")
    v.add_config_path(".")
    v.read_in_config()
    v.automatic_env()
    logging.config.dictConfig(v.get("LOGGING_CONF"))


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


app = FastAPI()
app.include_router(users.router)


# Logging init
logger = logging.getLogger(__name__)
logger.info("Starting server...")


@app.get("/")
async def root() -> Json[Any]:
    return {"message": "Hello World"}


def main() -> None:
    setup_vyper()

    uvicorn.run(app)


if __name__ == "__main__":
    main()
