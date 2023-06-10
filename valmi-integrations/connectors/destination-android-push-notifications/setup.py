from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "valmi_connector_lib",
    "requests",
    "firebase-admin",
    "jinja2"
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_android_push_notifications",
    description="Destination implementation for Android Push Notifications.",
    author="valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
