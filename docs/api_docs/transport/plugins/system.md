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
from io import BytesIO

from scrapli.exceptions import ScrapliConnectionNotOpened
from scrapli.transport.base import BaseTransportArgs
from scrapli.transport.plugins.system.transport import PluginTransportArgs, SystemTransport

# imported from base driver
_ = PluginTransportArgs


class NetconfSystemTransport(SystemTransport):
    def __init__(
        self, base_transport_args: BaseTransportArgs, plugin_transport_args: PluginTransportArgs
    ):
        self.write_chunk_size = 65535
        super().__init__(
            base_transport_args=base_transport_args, plugin_transport_args=plugin_transport_args
        )

    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        # adding `-tt` forces tty allocation which lets us send a string greater than 1024 chars;
        # without this we are basically capped at 1024 chars and scrapli will/the connection will
        # die. it *may* be possible to alter ptyprocess vendor'd code to add `stty -icanon` which
        # should also have a similar affect, though this seems simpler.
        self.open_cmd.extend(["-tt"])
        self.open_cmd.extend(["-s", "netconf"])
        self.logger.debug(f"final open_cmd: {self.open_cmd}")

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

    def write(self, channel_input: bytes) -> None:
        if not self.session:
            raise ScrapliConnectionNotOpened

        if self.write_chunk_size <= 0:
            self.session.write(channel_input)
        else:
            bytes_to_send_len = len(channel_input)
            bytes_to_send = BytesIO(channel_input)
            bytes_sent = 0

            while bytes_sent < bytes_to_send_len:
                self.session.write(bytes_to_send.read(self.write_chunk_size))
                bytes_sent += self.write_chunk_size
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
    def __init__(
        self, base_transport_args: BaseTransportArgs, plugin_transport_args: PluginTransportArgs
    ):
        self.write_chunk_size = 65535
        super().__init__(
            base_transport_args=base_transport_args, plugin_transport_args=plugin_transport_args
        )

    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        # adding `-tt` forces tty allocation which lets us send a string greater than 1024 chars;
        # without this we are basically capped at 1024 chars and scrapli will/the connection will
        # die. it *may* be possible to alter ptyprocess vendor'd code to add `stty -icanon` which
        # should also have a similar affect, though this seems simpler.
        self.open_cmd.extend(["-tt"])
        self.open_cmd.extend(["-s", "netconf"])
        self.logger.debug(f"final open_cmd: {self.open_cmd}")

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

    def write(self, channel_input: bytes) -> None:
        if not self.session:
            raise ScrapliConnectionNotOpened

        if self.write_chunk_size <= 0:
            self.session.write(channel_input)
        else:
            bytes_to_send_len = len(channel_input)
            bytes_to_send = BytesIO(channel_input)
            bytes_sent = 0

            while bytes_sent < bytes_to_send_len:
                self.session.write(bytes_to_send.read(self.write_chunk_size))
                bytes_sent += self.write_chunk_size
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



    

##### write
`write(self, channel_input: bytes) ‑> NoneType`

```text
Write bytes into the transport session

Args:
    channel_input: bytes to write to transport session

Returns:
    None

Raises:
    N/A
```