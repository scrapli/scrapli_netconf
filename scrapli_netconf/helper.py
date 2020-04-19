"""scrapli_netconf.helper"""
import re

from lxml import objectify
from lxml.etree import Element


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
