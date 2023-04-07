from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "requests",
    "customerio",
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_customer_io",
    description="Destination implementation for Customer.io .",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
