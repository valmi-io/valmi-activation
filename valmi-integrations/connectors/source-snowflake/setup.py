from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "dbt-snowflake",
    "fal==0.8.1",
    "jinja2",
    "valmi_connector_lib",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "connector-acceptance-test",
]

setup(
    name="source-snowflake",
    description="Source implementation for Snowflake.",
    author="Rajashekar Varkala @ valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
