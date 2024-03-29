from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import create_database, database_exists

from vyper import v
from contextlib import contextmanager

engine = create_engine(v.get_string("DATABASE_URL"), pool_pre_ping=True)


def validate_database():
    if not database_exists(engine.url):
        create_database(engine.url)


@lru_cache
def create_session() -> scoped_session:
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return Session


def get_session() -> Generator[scoped_session, None, None]:
    Session = create_session()
    try:
        yield Session
    finally:
        Session.remove()
