from setuptools import find_packages, setup

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
]


setup(
    name="valmi-activation",
    install_requires=install_requires,
    include_package_data=True,
    extras_require={"dev": ["flake8", "black", "mypy"]},
)
