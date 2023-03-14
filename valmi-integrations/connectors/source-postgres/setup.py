from setuptools import find_packages, setup
import os

MAIN_REQUIREMENTS = [
    "dbt-postgres==1.4.4",
    "fal==0.8.1",
    "jinja2",
    f"airbyte-cdk @ file://localhost/{os.getcwd()}/libs/airbyte_cdk-0.30.2-py3-none-any.whl",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "connector-acceptance-test",
]

setup(
    name="source-postgres",
    description="Source implementation for Postgres.",
    author="Rajashekar Varkala @ valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
