from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "valmi_connector_lib",
    "requests",
    "google-auth-oauthlib==0.5.1",
    "google-api-python-client==2.47.0",
    "google-ads==21.0.0"
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_google_ads",
    description="Destination implementation for Google Ads.",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
