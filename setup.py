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
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
)
