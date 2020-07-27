#!/usr/bin/env python
"""scrapli_netconf - netconf driver built on scrapli"""
import setuptools

__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="scrapli_netconf",
    version="2020.07.26",
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="Netconf driver built on scrapli",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/scrapli/scrapli_netconf",
    packages=setuptools.find_packages(),
    install_requires=["scrapli>=2020.07.26", "lxml>=4.5.1"],
    extras_require={},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
