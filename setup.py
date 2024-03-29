from setuptools import setup

install_requires = [
    "fastapi",
    "uvicorn",
    "pydantic[email]",
    "vyper-config",
    "tenacity",
    "dagster-graphql",
    "alembic",
    "starlette",
    "psycopg2-binary",
    "sqlalchemy-utils",
    "airbyte-cdk",
    "jinja2",
    "duckdb==0.7.1",
    "python-json-logger",
    "opentelemetry-instrumentation-fastapi",
    "opentelemetry-instrumentation-requests",
    "opentelemetry-exporter-otlp"
]


setup(
    name="valmi-activation",
    install_requires=install_requires,
    include_package_data=True,
    extras_require={"dev": ["flake8", "black", "mypy"]},
)
