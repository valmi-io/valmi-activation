from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "requests",
    "valmi_airbyte_cdk",
    "pydantic",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
]

setup(
    name="valmi_connector_lib",
    version="0.1.14",
    description="Connector library for valmi connectors.",
    long_description="Connector library for valmi connectors.",
    author="Rajashekar Varkala @ valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
