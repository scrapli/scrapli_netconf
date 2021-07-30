<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.helper

scrapli_netconf.helper

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.helper"""
import re
from logging import getLogger

from lxml import objectify
from lxml.etree import Element

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
        </code>
    </pre>
</details>



## Functions

    

#### remove_namespaces
`remove_namespaces(tree: <cyfunction Element at 0x7f85c00de860>) ‑> <cyfunction Element at 0x7f85c00de860>`

```text
Remove all namespace tags from Element object

Replace element tags like: {http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-bgp-oper}connection-state
With: connection-state

Args:
    tree: lxml Element

Returns:
    Element: lxml Element with namespaces stripped out

Raises:
    N/A
```