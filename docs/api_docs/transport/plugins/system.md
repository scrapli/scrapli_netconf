<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.transport.plugins.system.transport

scrapli_netconf.transport.plugins.system.transport

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.transport.plugins.system.transport"""
from scrapli.transport.plugins.system.transport import PluginTransportArgs, SystemTransport

# imported from base driver
_ = PluginTransportArgs


class NetconfSystemTransport(SystemTransport):
    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        self.open_cmd.extend(["-s", "netconf"])

    def open_netconf(self) -> None:
        """
        Netconf open method

        Simply calls the "normal" open method, but retaining an explicit "netconf" open for sanity

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.open()
        </code>
    </pre>
</details>



## Classes

### NetconfSystemTransport


```text
Helper class that provides a standard way to create an ABC using
inheritance.
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfSystemTransport(SystemTransport):
    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        self.open_cmd.extend(["-s", "netconf"])

    def open_netconf(self) -> None:
        """
        Netconf open method

        Simply calls the "normal" open method, but retaining an explicit "netconf" open for sanity

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.open()
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.transport.plugins.system.transport.SystemTransport
- scrapli.transport.base.sync_transport.Transport
- scrapli.transport.base.base_transport.BaseTransport
- abc.ABC
#### Methods

    

##### open_netconf
`open_netconf(self) ‑> NoneType`

```text
Netconf open method

Simply calls the "normal" open method, but retaining an explicit "netconf" open for sanity

Args:
    N/A

Returns:
    None

Raises:
    N/A
```