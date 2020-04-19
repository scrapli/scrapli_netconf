#!/usr/bin/env python
"""scrapli_netconf - netconf plugin for scrapli"""
import setuptools

__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="scrapli_netconf",
    version="2020.03.22",
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="Netconf plugin for scrapli",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/carlmontanari/scrapli_netconf",
    packages=setuptools.find_packages(),
    install_requires=["scrapli>=2020.03.21", "lxml>=4.5.0"],
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
