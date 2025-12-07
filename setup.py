"""
Setup script for Momentum Hub.

This file is kept for compatibility with older tools and direct pip install from git.
Modern installations should use pyproject.toml (PEP 517/518).
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="momentum-hub",
    version="1.0.0",
    author="Aaron Malunga",
    author_email="malungaron@gmail.com",
    description="A CLI habit tracker for building and maintaining daily/weekly habits.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaronmalunga/momentum-hub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=[
        "questionary>=1.10.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "pyfiglet>=0.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-mock>=3.14.0",
            "pytest-cov>=7.0.0",
            "coverage>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "momentum=momentum_main:main",
        ],
    },
)
