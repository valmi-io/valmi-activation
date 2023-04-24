from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["valmi_connector_lib", "requests"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_template",
    description="Destination implementation for template .",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
