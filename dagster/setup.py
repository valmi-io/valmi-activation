from setuptools import setup

install_requires = ["dagster", "dagster-docker"]


setup(
    name="valmi-repo",
    install_requires=install_requires,
    extras_require={"dev": ["flake8", "black", "mypy"]},
)
