from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["valmi_connector_lib", "requests", "slack_sdk", "jinja2"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_slack",
    description="Destination implementation for Slack .",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
