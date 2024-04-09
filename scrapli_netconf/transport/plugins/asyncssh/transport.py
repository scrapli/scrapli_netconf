"""scrapli_netconf.transport.plugins.asyncssh.transport"""

import asyncio
from typing import Any, Dict

from asyncssh.connection import SSHClientConnection, connect
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
        # hosts and agent to None so we can not have an agent and deal w/ known hosts ourselves.
        # to use ssh-agent either pass an empty tuple (to pick up ssh-agent socket from
        # SSH_AUTH_SOCK), or pass an explicit path to ssh-agent socket should be provided as part
        # of transport_options -- in either case these get merged into the dict *after* we set the
        # default value of `None`, so users options override our defaults.

        common_args: Dict[str, Any] = {
            "host": self._base_transport_args.host,
            "port": self._base_transport_args.port,
            "username": self.plugin_transport_args.auth_username,
            "known_hosts": None,
            "agent_path": None,
            "config": self.plugin_transport_args.ssh_config_file,
        }

        # Allow passing `transport_options` to asyncssh
        common_args.update(self._base_transport_args.transport_options.get("asyncssh", {}))

        # Common authentication args
        auth_args: Dict[str, Any] = {
            "client_keys": self.plugin_transport_args.auth_private_key,
            "password": self.plugin_transport_args.auth_password,
            "preferred_auth": (
                "publickey",
                "keyboard-interactive",
                "password",
            ),
        }

        # The session args to use in connect() - to merge the dicts in
        # the order to have transport options preference over predefined auth args
        conn_args = {**auth_args, **common_args}

        try:
            self.session: SSHClientConnection = await asyncio.wait_for(
                connect(**conn_args),
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
