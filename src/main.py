"""docs:  http://127.0.0.1:8000/docs"""
import logging
import logging.config

import uvicorn
from vyper import v
from app import create_app
from vyperconfig import setup_vyper

# Logging init
logger = logging.getLogger(v.get("LOGGER_NAME"))


def main() -> None:
    uvicorn.run(app())


def app():
    setup_vyper()
    logging.config.dictConfig(v.get("LOGGING_CONF"))
    logger.info("Starting server...")
    return create_app()


if __name__ == "__main__":
    main()
