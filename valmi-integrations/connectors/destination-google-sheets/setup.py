from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "valmi_connector_lib",
    "requests",
    "pygsheets==2.0.5",
    "google-auth-oauthlib==0.5.1",
    "google-api-python-client==2.47.0",
]

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
