"""docs:  http://127.0.0.1:8000/docs"""
import logging
import logging.config

import uvicorn
from fastapi import FastAPI
from vyper import v

from api.ctrls import users


def setup_vyper() -> None:
    v.set_config_type("yaml")
    v.set_config_name("config")
    v.add_config_path(".")
    v.read_in_config()
    v.automatic_env()
    logging.config.dictConfig(v.get("LOGGING_CONF"))


def main() -> None:
    setup_vyper()

    app = FastAPI()
    app.include_router(users.router)

    # Logging init
    logger = logging.getLogger(__name__)
    logger.info("Starting server...")

    uvicorn.run(app)


if __name__ == "__main__":
    main()
