"""scrapli_netconf.helper"""
import importlib
import re
from logging import getLogger
from typing import Any

from lxml import objectify
from lxml.etree import Element

from scrapli.exceptions import TransportPluginError

LOG = getLogger("scrapli_netconf.helper")


def remove_namespaces(tree: Element) -> Element:
    """
    Remove all namespace tags from Element object

    Replace element tags like: {http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-bgp-oper}connection-state
    With: connection-state

    Args:
        tree: lxml Element

    Returns:
        Element: lxml Element with namespaces stripped out

    Raises:
        N/A

    """
    for el in tree.getiterator():
        if not hasattr(el.tag, "find"):
            continue
        el.tag = re.sub(r"^{.*}", "", el.tag)
    objectify.deannotate(tree, cleanup_namespaces=True)
    return tree


def _find_netconf_transport_plugin(transport: str) -> Any:
    """
    Find non-core transport plugins and required plugin arguments

    Args:
        transport: string name of the desired transport, i.e.: paramiko or ssh2

    Returns:
        Any: class representing the given transport

    Raises:
        ModuleNotFoundError: if unable to  find scrapli transport module
        TransportPluginError: if unable to load `Transport` and `TRANSPORT_ARGS` from given
            transport module

    """
    try:
        importlib.import_module(f"scrapli_{transport}.transport")
    except ModuleNotFoundError as exc:
        err = f"Module '{exc.name}' not found!"
        msg = f"***** {err} {'*' * (80 - len(err))}"
        fix = (
            "To resolve this issue, ensure you are referencing a valid transport plugin. Transport"
            " plugins should be named similar to `scrapli_paramiko` or `scrapli_ssh2`, and can be "
            "selected by passing simply `paramiko` or `ssh2` into the scrapli driver. You can "
            "install most plugins with pip: `pip install scrapli-ssh2` for example."
        )
        warning = "\n" + msg + "\n" + fix + "\n" + msg
        LOG.warning(warning)
        raise ModuleNotFoundError(warning) from exc

    transport_package_names = {"ssh2": "cssh2", "paramiko": "miko", "asyncssh": "asyncssh_"}
    transport_class_names = {
        "ssh2": "NetconfSSH2Transport",
        "paramiko": "NetconfMikoTransport",
        "asyncssh": "NetconfAsyncSSHTransport",
    }
    netconf_transport_module = importlib.import_module(
        f"scrapli_netconf.transport.{transport_package_names.get(transport)}"
    )
    transport_class = getattr(netconf_transport_module, transport_class_names[transport], None)

    if not transport_class:
        msg = f"Failed to load transport plugin `{transport}` transport class"
        raise TransportPluginError(msg)

    return transport_class
