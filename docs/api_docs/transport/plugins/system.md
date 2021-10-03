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

        # JunOS devices do not allocate pty on port 830 on some (all?) platforms, users can cause
        # system transport to *not* force the pty (forcing pty is *default behavior*) by setting the
        # transport arg `netconf_force_pty` to `False`. This defaults to `True` (forcing a pty) as
        # that has been the default behavior for a while and seems to work in almost all cases,
        # additionally without this -- in pytest (only in pytest for some reason?) output seems to
        # come from devices out of order causing all the echo check logic to break... with this pty
        # being forced that seems to never occur. Worth digging into more at some point...
        if self._base_transport_args.transport_options.get("netconf_force_pty", True) is True:
            self.open_cmd.append("-tt")

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

System (i.e. /bin/ssh) transport plugin.

This transport supports some additional `transport_options` to control behavior --

`ptyprocess` is a dictionary that has the following options:
    rows: integer number of rows for ptyprocess "window"
    cols: integer number of cols for ptyprocess "window"
    echo: defaults to `True`, passing `False` disables echo in the ptyprocess; should only
        be used with scrapli-netconf, will break scrapli!

`netconf_force_pty` is a scrapli-netconf only argument. This setting defaults to `True` and
    allows you to *not* force a pty. This setting seems to only be necessary when connecting
    to juniper devices on port 830 as junos decides to not allocate a pty on that port for
    some reason!

Args:
    base_transport_args: scrapli base transport plugin arguments
    plugin_transport_args: system ssh specific transport plugin arguments

Returns:
    N/A

Raises:
    ScrapliUnsupportedPlatform: if system is windows
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

        # JunOS devices do not allocate pty on port 830 on some (all?) platforms, users can cause
        # system transport to *not* force the pty (forcing pty is *default behavior*) by setting the
        # transport arg `netconf_force_pty` to `False`. This defaults to `True` (forcing a pty) as
        # that has been the default behavior for a while and seems to work in almost all cases,
        # additionally without this -- in pytest (only in pytest for some reason?) output seems to
        # come from devices out of order causing all the echo check logic to break... with this pty
        # being forced that seems to never occur. Worth digging into more at some point...
        if self._base_transport_args.transport_options.get("netconf_force_pty", True) is True:
            self.open_cmd.append("-tt")

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