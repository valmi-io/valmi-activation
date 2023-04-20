from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "dbt-redshift==1.4.0",
    "fal==0.8.1",
    "jinja2",
    "valmi_connector_lib",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "connector-acceptance-test",
]

setup(
    name="source-redshift",
    description="Source implementation for Redshift.",
    author="Rajashekar Varkala @ valmi.io",
    author_email="contact@valmi.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
