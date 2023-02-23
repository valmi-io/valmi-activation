from setuptools import find_packages, setup

install_requires = ["dagster", "dagster-docker"]


setup(
    name="valmi-repo",
    install_requires=install_requires,
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(where="valmi_repo"),
    package_dir={"": "valmi_repo"},
    include_package_data=True,
    extras_require={"dev": ["flake8", "black", "mypy"]},
)
