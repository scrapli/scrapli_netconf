<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.transport.plugins.asyncssh.transport

scrapli_netconf.transport.plugins.asyncssh.transport

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.transport.plugins.asyncssh.transport"""
import asyncio

from asyncssh import connect
from asyncssh.connection import SSHClientConnection
from asyncssh.misc import ChannelOpenError, PermissionDenied

from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliConnectionNotOpened
from scrapli.transport.plugins.asyncssh.transport import AsyncsshTransport, PluginTransportArgs

# imported from base driver
_ = PluginTransportArgs


class NetconfAsyncsshTransport(AsyncsshTransport):
    async def open_netconf(self) -> None:
        """
        Netconf open method

        Simply calls the "normal" open method, but retaining an explicit "netconf" open for sanity

        Args:
            N/A

        Returns:
            None

        Raises:
            ScrapliAuthenticationFailed: if auth fails
            ScrapliConnectionNotOpened: if connection cant be opened (but is not an auth failure)

        """
        if self.plugin_transport_args.auth_strict_key:
            self.logger.debug(
                f"Attempting to validate {self._base_transport_args.host} public key is in known "
                f"hosts"
            )
            self._verify_key()

        # we already fetched host/port/user from the user input and/or the ssh config file, so we
        # want to use those explicitly. likewise we pass config file we already found. set known
        # hosts and agent to None so we can not have an agent and deal w/ known hosts ourselves
        common_args = {
            "host": self._base_transport_args.host,
            "port": self._base_transport_args.port,
            "username": self.plugin_transport_args.auth_username,
            "known_hosts": None,
            "agent_path": None,
            "config": self.plugin_transport_args.ssh_config_file,
        }

        try:
            self.session: SSHClientConnection = await asyncio.wait_for(
                connect(
                    client_keys=self.plugin_transport_args.auth_private_key,
                    password=self.plugin_transport_args.auth_password,
                    preferred_auth=(
                        "publickey",
                        "keyboard-interactive",
                        "password",
                    ),
                    **common_args,
                ),
                timeout=self._base_transport_args.timeout_socket,
            )
        except PermissionDenied as exc:
            msg = "all authentication methods failed"
            self.logger.critical(msg)
            raise ScrapliAuthenticationFailed(msg) from exc
        except asyncio.TimeoutError as exc:
            msg = "timed out opening connection to device"
            self.logger.critical(msg)
            raise ScrapliAuthenticationFailed(msg) from exc

        # it seems we must pass a terminal type to force a pty(?) which i think we want in like...
        # every case?? https://invisible-island.net/ncurses/ncurses.faq.html#xterm_color
        # set encoding to None so we get bytes for consistency w/ other scrapli transports
        # request_pty seems to be safe to set to "false" but leaving it at auto which seems closer
        # to the default behavior. With this omitted (as was previously) connecting to junos devices
        # on port 830 worked w/ system transport but *not* asyncssh because the pty request failed
        try:
            self.stdin, self.stdout, _ = await self.session.open_session(
                term_type="xterm", encoding=None, subsystem="netconf", request_pty="auto"
            )
        except ChannelOpenError as exc:
            msg = (
                "Failed to open Channel -- do you have the right port? Most often the netconf "
                "port is 22 or 830!"
            )
            self.logger.critical(msg)
            raise ScrapliConnectionNotOpened(msg) from exc

        if not self.session:
            raise ScrapliConnectionNotOpened

        if self.plugin_transport_args.auth_strict_key:
            self.logger.debug(
                f"Attempting to validate {self._base_transport_args.host} public key is in known "
                f"hosts and is valid"
            )
            self._verify_key_value()
        </code>
    </pre>
</details>



## Classes

### NetconfAsyncsshTransport


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
class NetconfAsyncsshTransport(AsyncsshTransport):
    async def open_netconf(self) -> None:
        """
        Netconf open method

        Simply calls the "normal" open method, but retaining an explicit "netconf" open for sanity

        Args:
            N/A

        Returns:
            None

        Raises:
            ScrapliAuthenticationFailed: if auth fails
            ScrapliConnectionNotOpened: if connection cant be opened (but is not an auth failure)

        """
        if self.plugin_transport_args.auth_strict_key:
            self.logger.debug(
                f"Attempting to validate {self._base_transport_args.host} public key is in known "
                f"hosts"
            )
            self._verify_key()

        # we already fetched host/port/user from the user input and/or the ssh config file, so we
        # want to use those explicitly. likewise we pass config file we already found. set known
        # hosts and agent to None so we can not have an agent and deal w/ known hosts ourselves
        common_args = {
            "host": self._base_transport_args.host,
            "port": self._base_transport_args.port,
            "username": self.plugin_transport_args.auth_username,
            "known_hosts": None,
            "agent_path": None,
            "config": self.plugin_transport_args.ssh_config_file,
        }

        try:
            self.session: SSHClientConnection = await asyncio.wait_for(
                connect(
                    client_keys=self.plugin_transport_args.auth_private_key,
                    password=self.plugin_transport_args.auth_password,
                    preferred_auth=(
                        "publickey",
                        "keyboard-interactive",
                        "password",
                    ),
                    **common_args,
                ),
                timeout=self._base_transport_args.timeout_socket,
            )
        except PermissionDenied as exc:
            msg = "all authentication methods failed"
            self.logger.critical(msg)
            raise ScrapliAuthenticationFailed(msg) from exc
        except asyncio.TimeoutError as exc:
            msg = "timed out opening connection to device"
            self.logger.critical(msg)
            raise ScrapliAuthenticationFailed(msg) from exc

        # it seems we must pass a terminal type to force a pty(?) which i think we want in like...
        # every case?? https://invisible-island.net/ncurses/ncurses.faq.html#xterm_color
        # set encoding to None so we get bytes for consistency w/ other scrapli transports
        # request_pty seems to be safe to set to "false" but leaving it at auto which seems closer
        # to the default behavior. With this omitted (as was previously) connecting to junos devices
        # on port 830 worked w/ system transport but *not* asyncssh because the pty request failed
        try:
            self.stdin, self.stdout, _ = await self.session.open_session(
                term_type="xterm", encoding=None, subsystem="netconf", request_pty="auto"
            )
        except ChannelOpenError as exc:
            msg = (
                "Failed to open Channel -- do you have the right port? Most often the netconf "
                "port is 22 or 830!"
            )
            self.logger.critical(msg)
            raise ScrapliConnectionNotOpened(msg) from exc

        if not self.session:
            raise ScrapliConnectionNotOpened

        if self.plugin_transport_args.auth_strict_key:
            self.logger.debug(
                f"Attempting to validate {self._base_transport_args.host} public key is in known "
                f"hosts and is valid"
            )
            self._verify_key_value()
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.transport.plugins.asyncssh.transport.AsyncsshTransport
- scrapli.transport.base.async_transport.AsyncTransport
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
    ScrapliAuthenticationFailed: if auth fails
    ScrapliConnectionNotOpened: if connection cant be opened (but is not an auth failure)
```