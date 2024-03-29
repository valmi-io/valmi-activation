from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["valmi-connector-lib", "requests", "flatten-json"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_gong",
    description="Destination implementation for Gong.",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
