from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "requests"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_webhook",
    description="Destination implementation for Webhook.",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
