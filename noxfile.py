"""scrapli_netconf.noxfile"""
import re
from pathlib import Path
from typing import Dict, List

import nox

nox.options.error_on_missing_interpreters = False
nox.options.stop_on_first_error = False

DEV_REQUIREMENTS: Dict[str, str] = {}

# this wouldn't work for other projects probably as its kinda hacky, but works just fine for scrapli
with open("requirements-dev.txt") as f:
    req_lines = f.readlines()
    dev_requirements_lines: List[str] = [
        line
        for line in req_lines
        if not line.startswith("-r") and not line.startswith("#") and not line.startswith("-e")
    ]
    dev_editable_requirements_lines: List[str] = [
        line for line in req_lines if line.startswith("-e")
    ]

for requirement in dev_requirements_lines:
    parsed_requirement = re.match(
        pattern=r"^([a-z0-9\-\_]+)([><=]{1,2}\S*)(?:.*)$", string=requirement, flags=re.I | re.M
    )
    DEV_REQUIREMENTS[parsed_requirement.groups()[0]] = parsed_requirement.groups()[1]

for requirement in dev_editable_requirements_lines:
    parsed_requirement = re.match(
        pattern=r"^-e\s.*(?:#egg=)(\w+)$", string=requirement, flags=re.I | re.M
    )
    DEV_REQUIREMENTS[parsed_requirement.groups()[0]] = requirement


@nox.session(python=["3.6", "3.7", "3.8", "3.9"])
def unit_tests(session):
    """
    Nox run unit tests

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install("-r", "requirements-dev.txt")
    # seems that pip thinks that it satisfies all extras when just installing scrapli, so it seems
    # we need to install these individually
    session.install("-r", "requirements-paramiko.txt")
    session.install("-r", "requirements-asyncssh.txt")
    session.install("-r", "requirements-ssh2.txt")
    session.run(
        "pytest",
        "--cov=scrapli_netconf",
        "--cov-report",
        "html",
        "--cov-report",
        "term",
        "tests/unit",
        "-v",
    )


@nox.session(python=["3.9"])
def isort(session):
    """
    Nox run isort

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install(f"isort{DEV_REQUIREMENTS['isort']}")
    session.run("isort", "-c", ".")


@nox.session(python=["3.9"])
def black(session):
    """
    Nox run black

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install(f"black{DEV_REQUIREMENTS['black']}")
    session.run("black", "--check", ".")


@nox.session(python=["3.9"])
def pylama(session):
    """
    Nox run pylama

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install("-e", ".")
    session.install("-r", "requirements-dev.txt")
    # pylama needs a few asyncssh exceptions imported to not fail
    session.install("-r", "requirements-asyncssh.txt")
    session.run("pylama", ".")


@nox.session(python=["3.9"])
def pydocstyle(session):
    """
    Nox run pydocstyle

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install(f"pydocstyle{DEV_REQUIREMENTS['pydocstyle']}")
    session.run("pydocstyle", ".")


@nox.session(python=["3.9"])
def mypy(session):
    """
    Nox run mypy

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install(f"mypy{DEV_REQUIREMENTS['mypy']}")
    session.install("-e", DEV_REQUIREMENTS["scrapli_stubs"].split()[1])
    session.env["MYPYPATH"] = f"{session.virtualenv.location}/src/scrapli-stubs"
    session.run("mypy", "--strict", "scrapli_netconf/")


@nox.session(python=["3.9"])
def darglint(session):
    """
    Nox run darglint

    Args:
        session: nox session

    Returns:
        N/A  # noqa: DAR202

    Raises:
        N/A

    """
    session.install(f"darglint{DEV_REQUIREMENTS['darglint']}")
    files_to_darglint = Path("scrapli_netconf").rglob("*.py")
    for file in files_to_darglint:
        session.run("darglint", f"{file.absolute()}")
