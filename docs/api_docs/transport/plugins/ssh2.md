<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.transport.plugins.ssh2.transport

scrapli_netconf.transport.plugins.ssh2.transport

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.transport.plugins.ssh2.transport"""
from scrapli.exceptions import ScrapliConnectionNotOpened
from scrapli.transport.plugins.ssh2.transport import PluginTransportArgs, Ssh2Transport

# imported from base driver
_ = PluginTransportArgs


class NetconfSsh2Transport(Ssh2Transport):
    def open_netconf(self) -> bytes:
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
        super().open()

        return b""

    def _open_channel(self) -> None:
        """
        Overriding the base open_channel to invoke netconf subsystem

        Args:
            N/A

        Returns:
            None

        Raises:
            ScrapliConnectionNotOpened: if session is unopened/None

        """
        if not self.session:
            raise ScrapliConnectionNotOpened

        self.session_channel = self.session.open_session()
        # unlike "normal" ssh2 -- we do *not* need to enable the "shell" on the channel...
        # we *do* still want it to be a pty though!
        self.session_channel.pty()
        self.session_channel.subsystem("netconf")

    def _get_channel_fd(self) -> int:
        """
        Function to get the fd to check for "echo" with

        Args:
             N/A

        Returns:
            int: fd of the channel

        Raises:
            N/A

        """
        channel_fd: int = self.socket.sock.fileno()
        return channel_fd
        </code>
    </pre>
</details>



## Classes

### NetconfSsh2Transport


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
class NetconfSsh2Transport(Ssh2Transport):
    def open_netconf(self) -> bytes:
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
        super().open()

        return b""

    def _open_channel(self) -> None:
        """
        Overriding the base open_channel to invoke netconf subsystem

        Args:
            N/A

        Returns:
            None

        Raises:
            ScrapliConnectionNotOpened: if session is unopened/None

        """
        if not self.session:
            raise ScrapliConnectionNotOpened

        self.session_channel = self.session.open_session()
        # unlike "normal" ssh2 -- we do *not* need to enable the "shell" on the channel...
        # we *do* still want it to be a pty though!
        self.session_channel.pty()
        self.session_channel.subsystem("netconf")

    def _get_channel_fd(self) -> int:
        """
        Function to get the fd to check for "echo" with

        Args:
             N/A

        Returns:
            int: fd of the channel

        Raises:
            N/A

        """
        channel_fd: int = self.socket.sock.fileno()
        return channel_fd
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.transport.plugins.ssh2.transport.Ssh2Transport
- scrapli.transport.base.sync_transport.Transport
- scrapli.transport.base.base_transport.BaseTransport
- abc.ABC
#### Methods

    

##### open_netconf
`open_netconf(self) ‑> bytes`

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