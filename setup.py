from setuptools import setup, find_packages
import io
import os


def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


setup(
    name="apisec-tester",
    version="0.1.0",
    description="Personal API Security Tester - lightweight API checks",
    long_description=read("README.md") if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=[
        "click>=8.1.7",
        "requests>=2.31.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "apisec-tester=cli:cli",
        ]
    },
    python_requires=">=3.8",
)
