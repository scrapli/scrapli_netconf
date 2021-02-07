<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.constants

scrapli_netconf.constants

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.constants"""
from enum import Enum


class NetconfVersion(Enum):
    UNKNOWN = "unknown"
    VERSION_1_0 = "1.0"
    VERSION_1_1 = "1.1"


class NetconfClientCapabilities(Enum):
    UNKNOWN = "unknown"
    CAPABILITIES_1_0 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
</hello>]]>]]>"""
    CAPABILITIES_1_1 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.1</capability>
        </capabilities>
</hello>]]>]]>"""
        </code>
    </pre>
</details>



## Classes

### NetconfClientCapabilities


```text
An enumeration.
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfClientCapabilities(Enum):
    UNKNOWN = "unknown"
    CAPABILITIES_1_0 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
</hello>]]>]]>"""
    CAPABILITIES_1_1 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.1</capability>
        </capabilities>
</hello>]]>]]>"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- enum.Enum
#### Class variables

    
`CAPABILITIES_1_0`




    
`CAPABILITIES_1_1`




    
`UNKNOWN`






### NetconfVersion


```text
An enumeration.
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfVersion(Enum):
    UNKNOWN = "unknown"
    VERSION_1_0 = "1.0"
    VERSION_1_1 = "1.1"
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- enum.Enum
#### Class variables

    
`UNKNOWN`




    
`VERSION_1_0`




    
`VERSION_1_1`