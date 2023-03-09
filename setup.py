from setuptools import setup

install_requires = [
    "fastapi",
    "uvicorn",
    "pydantic[email]",
    "vyper-config",
    "tenacity",
    "dagster-graphql",
    "alembic",
    "starlette ",
    "psycopg2-binary",
    "sqlalchemy-utils",
    "airbyte-cdk",
    "jinja2",
    "duckdb==0.7.1",
]


setup(
    name="valmi-activation",
    install_requires=install_requires,
    include_package_data=False,
    extras_require={"dev": ["flake8", "black", "mypy"]},
)
